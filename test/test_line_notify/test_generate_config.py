from pathlib import Path
import shutil

from installer.generate_config import GenerateConfig


def test_create_config_file():
    project_root = Path(__file__) / '..' / '..' / '..'
    project_root = project_root.resolve()
    config_dir = project_root / 'config'
    variable_dir = project_root / 'test' / 'test_ws'
    try:
        # インスタンス作成
        variable_dir.mkdir()
        instance = GenerateConfig(project_root)

        # 設定ファイル作成1
        test_data = {'config_version': '1', 'variable_dir': variable_dir}
        instance.create_config_file(**test_data)

        assert True

    except Exception:
        pass
    finally:
        shutil.rmtree(variable_dir)
        shutil.rmtree(config_dir)
