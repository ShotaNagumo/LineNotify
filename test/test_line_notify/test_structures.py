import pytest
from pathlib import Path
import shutil

from scripts.installer.generate_config import GenerateConfig

project_root: Path = Path(__file__) / '..' / '..' / '..'  # ./LineNotify
project_root = project_root.resolve()
template_dir = project_root / 'resource' / 'templates'

config_path = project_root / 'config' / 'config.yaml'
test_dir = project_root / 'test_ws' / 'test_structures'
test_dir_in = test_dir / 'input'
test_dir_out = test_dir / 'output'


def test_init(mocker):
    try:
        # 正常系
        gen_conf = GenerateConfig(template_dir)
        gen_conf.create_config_file(test_dir_out, Path('/var/opt/line_notify'))
        generated_data = Path(test_dir_out / 'config.yaml').read_text(encoding='utf-8')
        expect_data = Path(test_dir_in / 'config.yaml').read_text(encoding='utf-8')
        assert expect_data == generated_data

        # 異常系（TemplateNotFound発生）
        with (mocker.patch('pathlib.Path.mkdir', side_effect=Exception()), pytest.raises(Exception)):
            gen_conf = GenerateConfig(template_dir)
            gen_conf.create_config_file(test_dir_out, Path('/var/opt/line_notify'))

    except Exception as err:
        raise err

    finally:
        if test_dir_out.is_dir():
            shutil.rmtree(test_dir_out)
