import pytest
import re
from pathlib import Path
import shutil
import logging

from installer.generate_config import GenerateConfig
from line_notify.nagaoka_main import NagaokaMain


project_root = Path(__file__) / '..' / '..' / '..'
project_root = project_root.resolve()
config_dir = project_root / 'config'
variable_dir = project_root / 'test' / 'test_ws'
test_dir = project_root / 'test'
test_input_dir = test_dir / 'test_resource' / 'input'
test_expect_dir = test_dir / 'test_resource' / 'expect'


def test_download_page():
    try:
        # テスト用設定ファイル作成
        config_data = {'config_version': '1', 'variable_dir': variable_dir}
        gen_conf = GenerateConfig(project_root)
        gen_conf.create_config_file(**config_data)

        # インスタンス生成
        instance = NagaokaMain(project_root)
        assert True

#         # 設定ファイル作成確認1
#         with open(Path(test_expect_dir / 'config.1.yaml'), mode='rt', encoding='utf-8') as fp:
#             expect_data = fp.read()
#         with open(Path(config_dir / 'config.yaml'), mode='rt', encoding='utf-8') as fp:
#             generated_data = fp.read()
#         assert expect_data == generated_data
#         print(expect_data)

#         # 設定ファイル作成確認2（config_versionが不正）
#         test_data = {'config_version': '', 'variable_dir': variable_dir}
#         with pytest.raises(Exception, match=re.escape('Invalid argument. (config_version)')):
#             instance.create_config_file(**test_data)

#         # 設定ファイル作成確認3（variable_dirが不正）
#         test_data = {'config_version': '100', 'variable_dir': ''}
#         with pytest.raises(Exception, match=re.escape('Invalid argument. (variable_dir)')):
#             instance.create_config_file(**test_data)

    finally:
        # loggerを停止（この処理を行わないと、次のディレクトリ削除処理でエラーとなりテスト失敗する）
        logging.shutdown()

        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        if config_dir.exists():
            shutil.rmtree(config_dir)
