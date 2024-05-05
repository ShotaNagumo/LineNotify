from jinja2 import Template, Environment, FileSystemLoader
from pathlib import Path
from typing import Final


class CreateDotenv():
    VARIABLE_DIR_DEFAULT: Final[str] = ''

    def __init__(self):
        self._template_dir: Path = Path(__file__).parent
        self._dotenv_path: Path = Path(__file__).parent.parent.parent / 'line_notify' / '.env'

    def create(self, line_token_nagaoka: str, line_token_niigata: str, variable_dir=VARIABLE_DIR_DEFAULT):
        try:
            # Jinja2 Template セットアップ
            env: Final[Environment] = Environment(loader=FileSystemLoader(self._template_dir))
            template_data: Final[Template] = env.get_template('dotenv.j2')

            # dotenvデータ作成、出力
            export_data = {
                'variable_dir': variable_dir,
                'line_token_nagaoka': line_token_nagaoka,
                'line_token_niigata': line_token_niigata,
            }
            dotenv_data: Final[str] = template_data.render(export_data)
            self._dotenv_path.absolute().write_text(dotenv_data, encoding='utf-8')
            print(f'{dotenv_data=}')

        except Exception as err:
            # エラー発生時は呼び出し元にエラー発生を伝達
            print(f'{err=}')
            raise err
