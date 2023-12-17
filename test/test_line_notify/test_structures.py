import pytest
import re
from pathlib import Path
import shutil

from installer.generate_config import GenerateConfig
from line_notify.structures import MainClassSetting

project_root = Path(__file__) / '..' / '..' / '..'
project_root = project_root.resolve()
config_path = project_root / 'config' / 'config.yaml'
variable_dir = project_root / 'test' / 'test_ws'
test_dir = project_root / 'test'
test_input_dir = test_dir / 'test_resource' / 'input'
test_expect_dir = test_dir / 'test_resource' / 'expect'


def test_init(mocker):
    try:
        # テスト用設定ファイル作成
        config_data = {'config_version': '1', 'variable_dir': variable_dir}
        gen_conf = GenerateConfig(project_root)
        gen_conf.create_config_file(**config_data)

        # インスタンス生成確認1（成功）
        MainClassSetting(config_path)
        assert True

        # インスタンス生成確認2（設定ファイル構造エラー）
        copy_src = test_input_dir / 'test_structures_fail_1.yaml'
        shutil.copy(copy_src, config_path)
        with pytest.raises(Exception, match=re.escape('config.yaml format error.')):
            MainClassSetting(config_path)

        # インスタンス生成確認3（variable_dir生成エラー）
        gen_conf.create_config_file(**config_data)
        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        with mocker.patch('os.makedirs', side_effect=FileExistsError()):
            with pytest.raises(Exception, match=re.escape('config.yaml: variable_dir could not create.')):
                MainClassSetting(config_path)

    finally:
        if variable_dir.exists():
            shutil.rmtree(variable_dir)
        if config_path.parent.exists():
            shutil.rmtree(config_path.parent)
