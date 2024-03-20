import sqlite3
import re
import requests
from requests import ConnectionError, HTTPError, Timeout, RequestException
import unicodedata
import datetime
from logging import getLogger, Logger
from typing import Final
from pathlib import Path

from line_notify.logger_initializer import initialize_logger
from line_notify.errors import DownloadPageError, TextAnalysisError, DbOperationError, NotifyError
from line_notify.structures import MainClassSetting, DisasterTextType, DisasterTextInfo


class NagaokaMain:
    SITE_URL: Final[str] = 'http://www.nagaoka-fd.com/fire/saigai/saigaipc.html'
    NOTIFY_URL: Final[str] = 'https://notify-api.line.me/api/notify'

    def __init__(self):
        # ソフトウェア本体のパスを取得
        self._software_dir = Path(__file__).parent / '..'
        self._software_dir = Path.absolute(self._software_dir)

        # 設定値を読み取り
        setting_file_path: Final[Path] = self._software_dir / 'config' / 'config.yaml'
        settings = MainClassSetting(setting_file_path)
        self._variable_dir = settings.variable_dir

        # loggerを初期化し取得
        log_dir: Final[Path] = self._variable_dir / 'log'
        initialize_logger(self._software_dir, log_dir, 'line_notify_nagaoka')
        self._logger: Final[Logger] = getLogger('server_logger')

        # DBへのパスを取得
        self._master_db_path: Final[Path] = self._variable_dir / 'db' / 'line_notify_admin.db'
        self._data_db_path: Final[Path] = self._variable_dir / 'db' / 'line_notify_admin.db'

    def main(self):
        try:
            webpage_text: Final[str] = self._download_page()
            disaster_text_info_list = [
                dtext for dtext in self._trim_disaster_text(webpage_text) if self._is_new_disaster_text(dtext)
            ]

            for disaster_text_info in disaster_text_info_list:
                # 通知処理
                self._register_disaster_text(disaster_text_info)

        except Exception:
            pass

    def _download_page(self) -> str:
        # ダウンロード実行
        res: requests.Response = requests.Response()
        try:
            res = requests.get(NagaokaMain.SITE_URL)
            self._logger.debug(f'{res.status_code=}')
            res.raise_for_status()
        except ConnectionError:
            self._logger.exception('ConnectionError:')
            raise DownloadPageError('Faild to download webpage. (ConnectionError)')
        except HTTPError:
            self._logger.exception(f'HTTPError, response={res}:')
            raise DownloadPageError(f'Faild to download webpage. (HTTPError, status_code={res.status_code})')
        except Timeout:
            self._logger.exception('Timeout:')
            raise DownloadPageError('Faild to download webpage. (Timeout)')
        except RequestException:
            self._logger.exception('RequestException:')
            raise DownloadPageError('Faild to download webpage. (RequestException)')

        # ダウンロード成功時のテキスト整形処理
        res.encoding = 'sjis'
        text_data: str = unicodedata.normalize('NFKC', res.text)
        text_data = re.sub(r'\u3000', ' ', text_data)
        return text_data

    def _trim_disaster_text(self, webpage_text: str) -> list[DisasterTextInfo]:
        # 現在発生中の災害と終了した災害の一部（鎮圧、鎮火、消火不要、救助完了）を抜き出す
        disaster_text_list: list[DisasterTextInfo] = []

        # webpage_text をcurrentとpastに分解
        PAT = re.compile(
            r'.+↓現在発生している災害↓(.+)↑現在発生している災害↑.+↓過去の災害経過情報↓(.+)↑過去の災害経過情報↑.+',
            re.DOTALL
        )
        m = PAT.match(webpage_text)
        if not m:
            raise TextAnalysisError("ダウンロードしたWebページのフォーマットが異なります。")

        # 災害情報の文字列を抜き出す
        disaster_text_list.extend(self._trim_disaster_text_current(m.group(1)))
        disaster_text_list.extend(self._trim_disaster_text_past(m.group(2)))
        return disaster_text_list

    def _trim_disaster_text_current(self, webpage_text_current: str) -> list[DisasterTextInfo]:
        # 現在発生中の災害を抜き出す
        info_list = re.findall(r'(\d\d月\d\d日.+?出動しました。)', webpage_text_current, re.DOTALL)
        return [DisasterTextInfo(dinfo, DisasterTextType.CURRENT) for dinfo in info_list]

    def _trim_disaster_text_past(self, webpage_text_past: str) -> list[DisasterTextInfo]:
        # 終了した災害の一部（鎮圧、鎮火、消火不要、救助完了）を抜き出す
        disaster_list_past: list[DisasterTextInfo] = []

        # 鎮圧、鎮火、救助完了
        info_list = re.findall(r'(\d\d月\d\d日.+?は\d\d:\d\dに.+?しました。)', webpage_text_past)
        disaster_list_past.extend([DisasterTextInfo(dinfo, DisasterTextType.PAST_WITH_TIME) for dinfo in info_list])

        # 消火不要
        info_list = re.findall(r'(\d\d月\d\d日.+?は消火の必要はありませんでした。)', webpage_text_past)
        disaster_list_past.extend([DisasterTextInfo(dinfo, DisasterTextType.PAST) for dinfo in info_list])

        return disaster_list_past

    def _is_new_disaster_text(self, disaster_text_info: DisasterTextInfo) -> bool:
        try:
            # DBに接続
            conn: Final[sqlite3.Connection] = sqlite3.connect(self._db_file_path)
            cursor: Final[sqlite3.Cursor] = conn.cursor()

            # 登録済みであるか問い合わせ
            sql_tmpl = 'SELECT COUNT(*) FROM t_disaster_text_nagaoka WHERE disaster_text = ?;'
            values = (disaster_text_info.disaster_text, )
            count = cursor.execute(sql_tmpl, values).fetchone()[0]

            # DBから切断
            conn.commit()
            conn.close()

            return False if count == 0 else True

        except Exception as err:
            raise DbOperationError(err)

    def _register_disaster_text(self, disaster_text_info: DisasterTextInfo):
        try:
            # DBに接続
            conn: Final[sqlite3.Connection] = sqlite3.connect(self._db_file_path)
            cursor: Final[sqlite3.Cursor] = conn.cursor()

            # 登録
            sql_tmpl = 'INSERT INTO t_disaster_text_nagaoka (datetime, disaster_text) VALUES (?, ?);'
            values = (datetime.datetime.now(), disaster_text_info.disaster_text,)
            cursor.execute(sql_tmpl, values)

            # DBから切断
            conn.commit()
            conn.close()

        except Exception as err:
            raise DbOperationError(err)

    def _notify_to_line(self, access_token: str, message: str):
        # メッセージの投稿を実行
        res: requests.Response = requests.Response()
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            payload = {'message': message}
            res = requests.post(NagaokaMain.NOTIFY_URL, headers=headers, params=payload)
            self._logger.debug(f'{res.status_code=}')
            res.raise_for_status()
        except ConnectionError:
            self._logger.exception('ConnectionError:')
            raise NotifyError('Faild to post message. (ConnectionError)')
        except HTTPError:
            self._logger.exception(f'HTTPError, response={res}:')
            raise NotifyError(f'Faild to post message. (HTTPError, status_code={res.status_code})')
        except Timeout:
            self._logger.exception('Timeout:')
            raise NotifyError('Faild to post message. (Timeout)')
        except RequestException:
            self._logger.exception('RequestException:')
            raise NotifyError('Faild to post message. (RequestException)')
