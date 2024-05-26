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
    def getLnVariableDir(cls) -> Path | None:
        try:
            load_dotenv(cls.dotenv_path)
            varialble_dir_s = os.environ.get(KEY_VARIABLE_DIR)
            if varialble_dir_s is None:
                return None
            else:
                variable_dir_p = Path(varialble_dir_s)
                return variable_dir_p
        except Exception:
            return None

    @classmethod
    def getLnLineTokenNagaoka(cls) -> str | None:
        load_dotenv(cls.dotenv_path)
        return os.environ.get(KEY_LINE_TOKEN_NAGAOKA)

    @classmethod
    def getLnLineTokenNiigata(cls) -> str | None:
        load_dotenv(cls.dotenv_path)
        return os.environ.get(KEY_LINE_TOKEN_NIIGATA)
