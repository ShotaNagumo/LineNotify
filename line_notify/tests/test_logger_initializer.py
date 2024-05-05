from pathlib import Path
import logging
import pytest

from line_notify.src.logger_initializer import initialize_logger

template_dir = Path(__file__).parent.parent / 'resource' / 'templates'


@pytest.fixture
def create_log_dir(tmpdir):
    log_dir: Path = Path(tmpdir)
    yield log_dir


def test_initialize_logger_1(create_log_dir):
    try:
        # logger初期化確認1（成功）
        ret = initialize_logger(template_dir, create_log_dir, 'logger_test')
        assert ret is None

    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()


def test_initialize_logger_2(mocker, create_log_dir):
    try:
        # logger初期化確認2（失敗）
        with (mocker.patch('pathlib.Path.mkdir', side_effect=Exception()),
             pytest.raises(Exception)):
            initialize_logger(template_dir, create_log_dir, 'logger_test')

    finally:
        # loggerを停止
        logging.shutdown()
