from logging import config
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
import yaml
from typing import Final

from line_notify.src.ln_config import LnConfig


def initialize_logger(template_dir: Path, log_output_dir: Path):
    try:
        # ログ出力先ディレクトリを確認し、存在しない場合作成
        log_output_dir.mkdir(exist_ok=True)

        # Templateを読み込み
        env: Final[Environment] = Environment(loader=FileSystemLoader(template_dir))
        template_data: Final[Template] = env.get_template('log_format.j2')

        # 設定を作成
        setting_yaml: Final[str] = template_data.render(log_output_dir=log_output_dir)
        setting_data: dict = yaml.safe_load(setting_yaml)

        # 設定をloggingモジュールに反映
        config.dictConfig(setting_data)

    except Exception as err:
        print(f'Exception is occurred: {err}')
        raise err


def initialize_logger_auto():
    try:
        # ログ
        script_dir = Path(__file__).parent
        template_dir = script_dir.parent / 'resource' / 'templates'
        variable_dir: Path | None = LnConfig.getLnVariableDir()
        if variable_dir is None:
            # variable_dir が設定されていない場合は例外送出
            raise Exception('Log output directory is not defined.')
        else:
            log_output_dir = variable_dir / 'log'
            initialize_logger(template_dir, log_output_dir)

    except Exception as err:
        raise err
