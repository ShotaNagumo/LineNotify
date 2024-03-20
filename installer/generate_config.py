from jinja2 import Template, Environment, FileSystemLoader
from pathlib import Path
from typing import Final
import os


class GenerateConfig:
    TEMPLATE_FILE_NAME: Final[str] = 'config.j2'

    def __init__(self, project_root: Path):
        self._project_root: Final[Path] = project_root
        template_dir: Final[Path] = self._project_root / 'resource' / 'templates'
        self._env: Final[Environment] = Environment(loader=FileSystemLoader(template_dir))
        self._template_data: Final[Template] = self._env.get_template(GenerateConfig.TEMPLATE_FILE_NAME)

    def create_config_file(self, variable_dir: str):
        # 入力データチェック
        if variable_dir == '':
            raise Exception('Invalid argument. (variable_dir)')

        # 設定データを生成
        data = {
            'variable_dir': variable_dir,
        }
        settings: Final[str] = self._template_data.render(data)

        # 設定ファイルを書き込み
        config_dir = self._project_root / 'config'
        if not config_dir.exists():
            os.makedirs(config_dir)
        config_file_path = config_dir / 'config.yaml'
        with open(config_file_path, mode='wt', encoding='utf-8') as fp:
            fp.write(settings)
