from pathlib import Path
from typing import Final
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from line_notify.src.ln_config import LnConfig


# データベースファイルパスを決定
if (variable_dir_str := LnConfig.getLnVariableDir()) is None:
    raise ValueError("variable directory is not defined.")
db_file_path = Path(variable_dir_str) / 'db' / 'line_notify_data.db'
db_file_path.parent.mkdir(exist_ok=True)

# Engine, Session設定
DB_URL: Final[str] = f'sqlite:///{db_file_path.as_posix()}'
ENGINE = create_engine(DB_URL, echo=True)
SESSION = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


# sessionを取得する関数
@contextmanager
def session_factory():
    session = SESSION()
    try:
        yield session
        session.commit()
    except IntegrityError as ierr:
        print('Sqlalchemyエラー')
        session.rollback()
        raise ierr
    except Exception as err:
        session.rollback()
        raise err
    finally:
        session.close()


# sqlite 外部キー制約を強制するpragma
@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
