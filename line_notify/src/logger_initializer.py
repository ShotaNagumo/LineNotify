from logging import config
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
import yaml
from typing import Final


def initialize_logger(template_dir: Path, log_output_dir: Path, logger_name: str):
    try:
        # ログ出力先ディレクトリを確認し、存在しない場合作成
        log_output_dir.mkdir(exist_ok=True)

        # Templateを読み込み
        env: Final[Environment] = Environment(loader=FileSystemLoader(template_dir))
        template_data: Final[Template] = env.get_template('log_format.j2')

        # 設定を作成
        setting_yaml: Final[str] = template_data.render(logger_name=logger_name, log_output_dir=log_output_dir)
        setting_data: dict = yaml.safe_load(setting_yaml)

        # 設定をloggingモジュールに反映
        config.dictConfig(setting_data)

    except Exception as err:
        print(f'Exception is occurred: {err}')
        raise err
