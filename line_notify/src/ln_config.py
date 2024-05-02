from dotenv import load_dotenv
from pathlib import Path
from typing import Final
import os

KEY_VARIABLE_DIR: Final[str] = 'LN_VARIABLE_DIR'
KEY_LINE_TOKEN_NAGAOKA: Final[str] = 'LN_LINE_TOKEN_NAGAOKA'
KEY_LINE_TOKEN_NIIGATA: Final[str] = 'LN_LINE_TOKEN_NIIGATA'


class LnConfig:
    dotenv_path = Path(__file__).parent.parent / '.env'

    @classmethod
    def getLnVariableDir(cls) -> str | None:
        load_dotenv(cls.dotenv_path)
        return os.environ.get(KEY_VARIABLE_DIR)

    @classmethod
    def getLnLineTokenNagaoka(cls) -> str | None:
        load_dotenv(cls.dotenv_path)
        return os.environ.get(KEY_LINE_TOKEN_NAGAOKA)

    @classmethod
    def getLnLineTokenNiigata(cls) -> str | None:
        load_dotenv(cls.dotenv_path)
        return os.environ.get(KEY_LINE_TOKEN_NIIGATA)
