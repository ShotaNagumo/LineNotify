import pytest
import re
from pathlib import Path
import shutil
import logging
import requests

from scripts.installer.generate_config import GenerateConfig
from line_notify.src.nagaoka_main import NagaokaMain
from line_notify.src.structures import DisasterTextInfo, DisasterTextType
from line_notify.src.errors import DownloadPageError, NotifyError, TextAnalysisError


project_root = Path(__file__) / '..' / '..' / '..'
project_root = project_root.resolve()
config_dir = project_root / 'config'
variable_dir = project_root / 'test' / 'test_ws'
test_dir = project_root / 'test'
test_input_dir = test_dir / 'test_resource' / 'input'
test_expect_dir = test_dir / 'test_resource' / 'expect'


def test_download_page(mocker):
    try:
        # テスト用設定ファイル作成
        config_data = {'config_version': '1', 'variable_dir': variable_dir}
        gen_conf = GenerateConfig(project_root)
        gen_conf.create_config_file(**config_data)

        # インスタンス生成
        instance = NagaokaMain(project_root)

        # ダウンロードに成功するケース
        # テスト入力データ読み込み
        testdata_file_input = test_input_dir / 'webtext_1.txt'
        with open(testdata_file_input, mode='rt', encoding='sjis') as fp:
            testdata_in = fp.read()
        res = requests.Response()
        res._content = str.encode(testdata_in, encoding='sjis')
        res.status_code = 200

        # テスト正解データ読み込み
        testdata_file_expect = test_expect_dir / 'webtext_1.txt'
        with open(testdata_file_expect, mode='rt', encoding='utf-8') as fp:
            testdata_expect = fp.read()

        # check
        with mocker.patch('requests.get', return_value=res):
            ret = instance._download_page()
            assert testdata_expect == ret

        # ConnectionError
        with mocker.patch('requests.get', side_effect=requests.ConnectionError()):
            with pytest.raises(DownloadPageError, match=re.escape('Faild to download webpage. (ConnectionError)')):
                instance._download_page()

        # Timeout
        with mocker.patch('requests.get', side_effect=requests.Timeout()):
            with pytest.raises(DownloadPageError, match=re.escape('Faild to download webpage. (Timeout)')):
                instance._download_page()

        # RequestsException
        with mocker.patch('requests.get', side_effect=requests.RequestException()):
            with pytest.raises(DownloadPageError, match=re.escape('Faild to download webpage. (RequestException)')):
                instance._download_page()

        # HTTPError
        res = requests.Response()
        res.status_code = 400
        with mocker.patch('requests.get', return_value=res):
            with pytest.raises(DownloadPageError):
                instance._download_page()

    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        if config_dir.exists():
            shutil.rmtree(config_dir)


def test_notify_to_line(mocker):
    try:
        # テスト用設定ファイル作成
        config_data = {'config_version': '1', 'variable_dir': variable_dir}
        gen_conf = GenerateConfig(project_root)
        gen_conf.create_config_file(**config_data)

        # インスタンス生成
        instance = NagaokaMain(project_root)

        # ConnectionError
        with mocker.patch('requests.post', side_effect=requests.ConnectionError()):
            with pytest.raises(NotifyError, match=re.escape('Faild to post message. (ConnectionError)')):
                instance._notify_to_line('dummy_token', 'dummy_msg')

        # Timeout
        with mocker.patch('requests.post', side_effect=requests.Timeout()):
            with pytest.raises(NotifyError, match=re.escape('Faild to post message. (Timeout)')):
                instance._notify_to_line('dummy_token', 'dummy_msg')

        # RequestsException
        with mocker.patch('requests.post', side_effect=requests.RequestException()):
            with pytest.raises(NotifyError, match=re.escape('Faild to post message. (RequestException)')):
                instance._notify_to_line('dummy_token', 'dummy_msg')

        # HTTPError
        res = requests.Response()
        res.status_code = 400
        with mocker.patch('requests.post', return_value=res):
            with pytest.raises(NotifyError):
                instance._notify_to_line('dummy_token', 'dummy_msg')

    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        if config_dir.exists():
            shutil.rmtree(config_dir)


def test_trim_disaster_text_1():
    try:
        # テスト用設定ファイル作成
        config_data = {'config_version': '1', 'variable_dir': variable_dir}
        gen_conf = GenerateConfig(project_root)
        gen_conf.create_config_file(**config_data)

        # 入力データを読み取り
        testdata_file_input = test_input_dir / 'webtext_2.txt'
        with open(testdata_file_input, mode='rt', encoding='utf-8') as fp:
            testdata_in = fp.read()

        # 正解データ
        dataset = (
            ('12月21日 15:19 長岡市 二日町 に車両火災のため消防車が出動しました。', DisasterTextType.CURERNT),
            ('12月21日 15:01 長岡市 与板町与板 にガス漏れ警戒のため消防車が出動しました。', DisasterTextType.CURERNT),
            ('12月21日 13:48 長岡市 中島 6丁目に救急活動のため消防車が出動しました。', DisasterTextType.CURERNT),
            ('12月21日 11:50 長岡市 小国町千谷沢 の救助活動は12:05に救助終了しました。', DisasterTextType.PAST_WITH_TIME),
            ('12月08日 01:06 長岡市 小国町横沢 の建物火災は01:31に鎮火しました。', DisasterTextType.PAST_WITH_TIME),
            ('12月08日 01:06 長岡市 小国町横沢 の建物火災は01:28に鎮圧しました。', DisasterTextType.PAST_WITH_TIME),
            ('12月16日 08:39 長岡市 寺泊 薮田の病院火災は消火の必要はありませんでした。', DisasterTextType.PAST),
        )
        expect = [DisasterTextInfo(*arg) for arg in dataset]

        # インスタンス生成
        instance = NagaokaMain(project_root)

        # 切り抜き確認
        ret = instance._trim_disaster_text(testdata_in)
        assert expect == ret
    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        if config_dir.exists():
            shutil.rmtree(config_dir)


def test_trim_disaster_text_2():
    try:
        # テスト用設定ファイル作成
        config_data = {'config_version': '1', 'variable_dir': variable_dir}
        gen_conf = GenerateConfig(project_root)
        gen_conf.create_config_file(**config_data)

        # 入力データを読み取り
        testdata_file_input = test_input_dir / 'webtext_3.txt'
        with open(testdata_file_input, mode='rt', encoding='utf-8') as fp:
            testdata_in = fp.read()

        # 正解データ
        dataset = (
            ('12月21日 11:50 長岡市 小国町千谷沢 の救助活動は12:05に救助終了しました。', DisasterTextType.PAST_WITH_TIME),
            ('12月08日 01:06 長岡市 小国町横沢 の建物火災は01:31に鎮火しました。', DisasterTextType.PAST_WITH_TIME),
            ('12月08日 01:06 長岡市 小国町横沢 の建物火災は01:28に鎮圧しました。', DisasterTextType.PAST_WITH_TIME),
            ('12月16日 08:39 長岡市 寺泊 薮田の病院火災は消火の必要はありませんでした。', DisasterTextType.PAST),
        )
        expect = [DisasterTextInfo(*arg) for arg in dataset]

        # インスタンス生成
        instance = NagaokaMain(project_root)

        # 切り抜き確認
        ret = instance._trim_disaster_text(testdata_in)
        assert expect == ret
    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        if config_dir.exists():
            shutil.rmtree(config_dir)


def test_trim_disaster_text_3():
    try:
        # テスト用設定ファイル作成
        config_data = {'config_version': '1', 'variable_dir': variable_dir}
        gen_conf = GenerateConfig(project_root)
        gen_conf.create_config_file(**config_data)

        # インスタンス生成
        instance = NagaokaMain(project_root)

        # webpage_text の内容が想定と異なる場合にExceptionが発生することを確認
        with pytest.raises(TextAnalysisError, match=re.escape('ダウンロードしたWebページのフォーマットが異なります。')):
            _ = instance._trim_disaster_text('')
    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        if config_dir.exists():
            shutil.rmtree(config_dir)
