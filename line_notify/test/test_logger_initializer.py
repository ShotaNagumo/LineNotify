from pathlib import Path
import shutil
import logging

from line_notify.logger_initializer import initialize_logger


def test_initialize_logger_1():
    project_root = Path(__file__) / '..' / '..' / '..'
    project_root = project_root.resolve()
    variable_dir = project_root / 'test' / 'test_ws1'
    log_dir = variable_dir / 'log'

    try:
        # logger初期化確認1（成功）
        ret = initialize_logger(project_root, log_dir, 'logger_test')
        assert ret

    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        if variable_dir.exists():
            shutil.rmtree(variable_dir)


def test_initialize_logger_2(mocker):
    project_root = Path(__file__) / '..' / '..' / '..'
    project_root = project_root.resolve()
    variable_dir = project_root / 'test' / 'test_ws2'
    log_dir = variable_dir / 'log'

    try:
        # logger初期化確認2（失敗）
        with mocker.patch('os.makedirs', side_effect=Exception()):
            ret = initialize_logger(project_root, log_dir, 'logger_test')
        assert not ret

    finally:
        # loggerを停止
        logging.shutdown()
