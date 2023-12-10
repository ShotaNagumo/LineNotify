import sqlite3
import re
import os
import requests
import unicodedata
import datetime
from logging import getLogger, Logger
import glob
from typing import Final
from pathlib import Path

from logger_initializer import initialize_logger
from errors import DownloadPageError, TextAnalysisError, DbOperationError
from structures import DisasterTextInfo, DisasterTextType


class NagaokaMain:
    SITE_URL: Final[str] = 'http://www.nagaoka-fd.com/fire/saigai/saigaipc.html'
    NOTIFY_URL: Final[str] = 'https://notify-api.line.me/api/notify'

    def __init__(self):
        # loggerを初期化し取得
        initialize_logger('nagaoka')
        self._logger: Final[Logger] = getLogger('server_logger')
        self._db_file_path: Final[Path] = Path()

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
        res: Final[requests.Response] = requests.get(NagaokaMain.SITE_URL)
        if res.status_code != 200:
            # ダウンロード失敗時のエラー処理
            self._logger.warning(f'Faild to download webpage. (status_code={res.status_code})')
            raise DownloadPageError(f'Faild to download webpage. (status_code={res.status_code})')
        else:
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
        return [DisasterTextInfo(dinfo, DisasterTextType.CURERNT) for dinfo in info_list]

    def _trim_disaster_text_past(self, webpage_text_past: str) -> list[DisasterTextInfo]:
        # 終了した災害の一部（鎮圧、鎮火、消火不要、救助完了）を抜き出す
        disaster_list_past: list[DisasterTextInfo] = []

        # 鎮圧、鎮火、救助完了
        info_list = re.findall(r'(\d\d月\d\d日.+?は\d\d:\d\dに.+?しました。)', webpage_text_past, re.DOTALL)
        disaster_list_past.extend([DisasterTextInfo(dinfo, DisasterTextType.PAST_WITH_TIME) for dinfo in info_list])

        # 消火不要
        info_list = re.findall(r'(\d\d月\d\d日.+?は消火の必要はありませんでした。)', webpage_text_past, re.DOTALL)
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
