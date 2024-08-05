from pathlib import Path
import logging
import pytest
import shutil

from line_notify.src.logger_initializer import initialize_logger, initialize_logger_auto


template_dir = Path(__file__).parent.parent / 'resource' / 'templates'
test_dir = Path(__file__).parent / '.testdir'


@pytest.fixture
def create_temp_dir():
    # テストディレクトリ作成
    test_dir.mkdir(exist_ok=True)
    yield
    # テストディレクトリ削除
    shutil.rmtree(test_dir)


@pytest.fixture
def logging_shutdown():
    yield
    logging.shutdown()


def test_initialize_logger_1(create_temp_dir, logging_shutdown):
    # logger初期化確認1（成功）
    ret = initialize_logger(template_dir, test_dir)
    assert ret is None


def test_initialize_logger_2(create_temp_dir, mocker, logging_shutdown):
    # logger初期化確認2（失敗）
    with (mocker.patch('pathlib.Path.mkdir', side_effect=Exception()),
            pytest.raises(Exception)):
        initialize_logger(template_dir, test_dir)


def test_initialize_logger_auto_1(create_temp_dir, mocker, logging_shutdown):
    # logger初期化確認1（成功）
    with mocker.patch('line_notify.src.ln_config.LnConfig.getLnVariableDir', return_value=test_dir):
        ret = initialize_logger_auto()
        assert ret is None


def test_initialize_logger_auto_2(create_temp_dir, mocker, logging_shutdown):
    # logger初期化確認2（失敗）
    with (mocker.patch('line_notify.src.ln_config.LnConfig.getLnVariableDir', return_value=None),
            pytest.raises(Exception)):
        initialize_logger_auto()
