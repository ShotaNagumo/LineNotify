import pytest
import src.ln_config
import os
from pathlib import Path


@pytest.fixture
def create_empty_dotenv():
    dotenv_path = Path(__file__).parent.parent / '.env'
    dotenv_path.touch()
    yield
    os.remove(dotenv_path)


@pytest.fixture
def create_dotenv():
    dotenv_path = Path(__file__).parent.parent / '.env'
    dotenv_path.touch()
    dotenv_path.write_text(
        'LN_VARIABLE_DIR=/x/y/z\n'
        'LN_LINE_TOKEN_NAGAOKA=YYY\n'
        'LN_LINE_TOKEN_NIIGATA=ZZZ\n'
    )
    yield
    os.remove(dotenv_path)


def test_dotenv_empty(create_empty_dotenv):
    assert src.ln_config.LnConfig.getLnVariableDir() is None
    assert src.ln_config.LnConfig.getLnLineTokenNagaoka() is None
    assert src.ln_config.LnConfig.getLnLineTokenNiigata() is None


def test_dotenv(create_dotenv):
    assert Path('/x/y/z') == src.ln_config.LnConfig.getLnVariableDir()
    assert 'YYY' == src.ln_config.LnConfig.getLnLineTokenNagaoka()
    assert 'ZZZ' == src.ln_config.LnConfig.getLnLineTokenNiigata()
