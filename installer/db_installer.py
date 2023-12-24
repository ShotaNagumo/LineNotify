from pathlib import Path
import argparse
import sqlite3
from typing import Final


def init_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument('variable_dir')
    parser.add_argument('mode', choices=['initialize', 'update', ])
    parser.add_argument('new_version', type=int)

    return parser


def db_initialize(database_file_path: Path):
    conn: Final[sqlite3.Connection] = sqlite3.connect(database_file_path)
    cursor: Final[sqlite3.Cursor] = conn.cursor()

    # システム情報を格納するテーブルを作成し、バージョン情報を登録
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS t_system (\n'
        'key TEXT PRIMARY KEY,\n'
        'value TEXT\n'
        ');'
    )
    conn.commit()
    cursor.execute(
        'INSERT INTO t_system VALUES ("db_format_version", "0");'
    )
    conn.commit()

    # token管理テーブルを作成
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS t_line_notify_token (\n'
        'city_name TEXT PRIMARY KEY,\n'
        'token TEXT NOT NULL\n'
        ');'
    )
    conn.commit()

    # 市ごとのデータ管理テーブルを作成
    cities = ['niigata', 'nagaoka',]
    for city_name in cities:
        cursor.execute(
            f'CREATE TABLE IF NOT EXISTS t_disaster_text_{city_name} (\n'
            'id INTEGER PRIMARY KEY AUTOINCREMENT,\n'
            'datetime TIMESTAMP NOT NULL,\n'
            'disaster_text TEXT NOT NULL\n'
            ');'
        )
        conn.commit()


def db_update(database_file_path: Path, new_version: int):
    pass


def execute(args):
    variable_path = Path(args.variable_dir)
    database_file_path = variable_path / 'database' / 'line_notify.db'
    database_file_path.parent.mkdir(exist_ok=True)

    if args.mode == 'initialize':
        db_initialize(database_file_path)
    elif args.mode == 'update':
        db_update(database_file_path, args.new_version)
    else:
        print('"mode" is invalid.')


if __name__ == '__main__':
    parser = init_argparser()
    args = parser.parse_args()
    execute(args)
