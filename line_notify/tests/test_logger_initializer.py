from pathlib import Path
import logging
import pytest
import shutil

from line_notify.src.logger_initializer import initialize_logger, initialize_logger_auto


template_dir = Path(__file__).parent.parent / 'resource' / 'templates'
test_dir = Path(__file__).parent / '.testdir'


def test_initialize_logger_1():
    try:
        # テストディレクトリ作成
        test_dir.mkdir(exist_ok=True)

        # logger初期化確認1（成功）
        ret = initialize_logger(template_dir, test_dir)
        assert ret is None

    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        # テストディレクトリ削除
        shutil.rmtree(test_dir)


def test_initialize_logger_2(mocker):
    try:
        # テストディレクトリ作成
        test_dir.mkdir(exist_ok=True)

        # logger初期化確認2（失敗）
        with (mocker.patch('pathlib.Path.mkdir', side_effect=Exception()),
             pytest.raises(Exception)):
            initialize_logger(template_dir, test_dir)

    finally:
        # loggerを停止
        logging.shutdown()

        # テストディレクトリ削除
        shutil.rmtree(test_dir)


def test_initialize_logger_auto_1(mocker):
    try:
        # テストディレクトリ作成
        test_dir.mkdir(exist_ok=True)

        # logger初期化確認1（成功）
        with mocker.patch('line_notify.src.ln_config.LnConfig.getLnVariableDir', return_value=test_dir):
            ret = initialize_logger_auto()
            assert ret is None

    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        # テストディレクトリ削除
        shutil.rmtree(test_dir)


def test_initialize_logger_auto_2(mocker):
    try:
        # テストディレクトリ作成
        test_dir.mkdir(exist_ok=True)

        # logger初期化確認2（失敗）
        with (mocker.patch('line_notify.src.ln_config.LnConfig.getLnVariableDir', return_value=None),
              pytest.raises(Exception)):
            initialize_logger_auto()

    finally:
        # loggerを停止
        logging.shutdown()

        # テストディレクトリ削除
        shutil.rmtree(test_dir)
