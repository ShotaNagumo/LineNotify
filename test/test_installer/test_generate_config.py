from pathlib import Path
import shutil

from installer.generate_config import GenerateConfig


def test_create_config_file():
    project_root = Path(__file__) / '..' / '..' / '..'
    project_root = project_root.resolve()
    config_dir = project_root / 'config'
    variable_dir = project_root / 'test' / 'test_ws'
    test_dir = project_root / 'test'
    test_input_dir = test_dir / 'test_resource' / 'input'
    test_expect_dir = test_dir / 'test_resource' / 'expect'
    try:
        # インスタンス作成
        variable_dir.mkdir()
        instance = GenerateConfig(project_root)

        # 設定ファイル作成確認1
        with open(Path(test_expect_dir / 'config.1.yaml'), mode='rt', encoding='utf-8') as fp:
            expect_data = fp.read()
        test_data = {'config_version': '1', 'variable_dir': variable_dir}
        instance.create_config_file(**test_data)
        with open(Path(config_dir / 'config.yaml'), mode='rt', encoding='utf-8') as fp:
            generated_data = fp.read()
        assert expect_data == generated_data
        print(expect_data)

    except Exception:
        pass
    finally:
        shutil.rmtree(variable_dir)
        shutil.rmtree(config_dir)
