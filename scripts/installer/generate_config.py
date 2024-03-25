from jinja2 import Template, Environment, FileSystemLoader
from pathlib import Path
from typing import Final


class GenerateConfig:
    TEMPLATE_FILE_NAME: Final[str] = 'config.j2'

    def __init__(self, template_dir: Path):
        env: Final[Environment] = Environment(loader=FileSystemLoader(template_dir))
        self._template_data: Final[Template] = env.get_template(GenerateConfig.TEMPLATE_FILE_NAME)

    def create_config_file(self, output_dir: Path, variable_dir: Path):
        try:
            # 出力ディレクトリ生成
            output_dir.mkdir(parents=True, exist_ok=True)

            # 書き込むデータを生成
            data = {
                'variable_dir': str(variable_dir),
            }
            settings: Final[str] = self._template_data.render(data)

            # 設定ファイルを生成
            config_file_path = output_dir / 'config.yaml'
            config_file_path.write_text(settings, encoding='utf-8')

        except Exception as err:
            raise err
