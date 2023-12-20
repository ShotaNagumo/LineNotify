import pytest
import re
from pathlib import Path
import shutil
import logging
import requests

from installer.generate_config import GenerateConfig
from line_notify.nagaoka_main import NagaokaMain
from line_notify.errors import DownloadPageError, NotifyError


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
