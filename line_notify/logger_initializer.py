from logging import config
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
import yaml
import os
from typing import Final


def initialize_logger(project_root: Path, log_output_dir: Path, logger_name: str) -> bool:
    try:
        # ログ出力先ディレクトリを確認し、存在しない場合作成
        if not log_output_dir.exists():
            os.makedirs(log_output_dir)

        # Templateを読み込み
        template_dir: Final[Path] = project_root / 'resource' / 'templates'
        env: Final[Environment] = Environment(loader=FileSystemLoader(template_dir))
        template_data: Final[Template] = env.get_template('log_format.j2')

        # 設定を作成
        settings: Final[str] = template_data.render(logger_name=logger_name, log_output_dir=log_output_dir)
        setting_data: dict = yaml.safe_load(settings)

        # 設定をloggingモジュールに反映
        config.dictConfig(setting_data)

    except Exception as err:
        print(f'Exception is occurred: {err}')
        return False

    return True
