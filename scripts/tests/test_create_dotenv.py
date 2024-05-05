from scripts.installer.create_dotenv import CreateDotenv
import pytest


def test_create_success():
    createDotenv = CreateDotenv()
    try:
        expect_data = 'LN_VARIABLE_DIR=ccc\nLN_LINE_TOKEN_NAGAOKA=aaa\nLN_LINE_TOKEN_NIIGATA=bbb'
        createDotenv.create('aaa', 'bbb', 'ccc')
        assert createDotenv._dotenv_path.exists()
        assert createDotenv._dotenv_path.read_text() == expect_data

    finally:
        createDotenv._dotenv_path.unlink()


def test_create_abort(mocker):
    createDotenv = CreateDotenv()
    try:
        with (mocker.patch('jinja2.Environment.get_template', side_effect=Exception()), pytest.raises(Exception)):
            createDotenv.create('aaa', 'bbb', 'ccc')

    finally:
        pass
