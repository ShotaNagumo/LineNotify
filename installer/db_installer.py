from pathlib import Path
import argparse
import sqlite3
import contextlib
import yaml
from typing import Union


def init_argparser():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()

    parser_initialize = sub_parsers.add_parser('initialize')
    parser_initialize.add_argument('database_dir')
    parser_initialize.set_defaults(func=db_initialize)

    parser_register_master = sub_parsers.add_parser('register_master')
    parser_register_master.add_argument('database_dir')
    parser_register_master.add_argument('master_data_path')
    parser_register_master.set_defaults(func=register_master)

    return parser


def db_initialize(args):
    # DBに接続
    try:
        # データベースファイルが入るディレクトリを読み取り・生成
        database_dir: Path = Path(args.database_dir)
        database_dir.mkdir(exist_ok=True)

        # admin情報を格納するデータベースファイル作成
        db_admin_path = database_dir / 'line_notify_admin.db'
        with contextlib.closing(sqlite3.connect(db_admin_path)) as conn:
            with conn as cur:
                # ソフトウェア情報
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_system (\n'
                    'key TEXT PRIMARY KEY,\n'
                    'value TEXT\n'
                    ');'
                )
                # Line Notify アクセストークン
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_line_access_token (\n'
                    'city_name TEXT PRIMARY KEY,\n'
                    'token TEXT NOT NULL\n'
                    ');'
                )

        # 災害情報を格納するデータベースファイル作成
        db_disaster_data_path = database_dir / 'line_notify_data.db'
        with contextlib.closing(sqlite3.connect(db_disaster_data_path)) as conn:
            with conn as cur:
                # 災害テキスト（解析前）
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_disaster_text (\n'
                    'disaster_id INTEGER PRIMARY KEY AUTOINCREMENT,\n'
                    'created_at TEXT DEFAULT (DATETIME(\'now\', \'localtime\')),\n'
                    'city_name REFERENCES t_city_name(rowid),\n'
                    'disaster_text TEXT NOT NULL,\n'
                    'line_notified INTEGER NOT NULL DEFAULT 0\n'
                    ');'
                )

                # 災害テキスト（解析後）
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_disaster_data (\n'
                    'disaster_id REFERENCES t_disaster_text(disaster_id),\n'
                    'open_month INTEGER NOT NULL,\n'
                    'open_day INTEGER NOT NULL,\n'
                    'open_hour INTEGER NOT NULL,\n'
                    'open_minute INTEGER NOT NULL,\n'
                    'disaster_category REFERENCES t_disaster_category(disaster_category),\n'
                    'disaster_status REFERENCES t_disaster_status(disaster_status),\n'
                    'address_district REFERENCES t_district(address_district),\n'
                    'address TEXT NOT NULL,\n'
                    'close_time TEXT\n'
                    ');'
                )

                # 都市名マスタ
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_city_name (\n'
                    'city_name TEXT PRIMARY KEY\n'
                    ');'
                )

                # 災害種別マスタ
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_disaster_category (\n'
                    'disaster_category TEXT PRIMARY KEY\n'
                    ');'
                )

                # 災害状態マスタ
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_disaster_status (\n'
                    'disaster_status TEXT PRIMARY KEY\n'
                    ');'
                )

                # 地区マスタ
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_district (\n'
                    'address_district TEXT PRIMARY KEY\n'
                    ');'
                )

    except Exception as err:
        print(f'ERROR: {err}')


def register_master(args):
    try:
        database_dir: Path = Path(args.database_dir)
        master_file_path: Path = Path(args.master_data_path)
        config = yaml.safe_load(master_file_path.read_text(encoding='utf-8'))
        # DBファイルループ
        for db_file in config:
            db_file_path = database_dir / f'line_notify_{db_file}.db'
            # tableループ
            for table in config.get(db_file):
                table_name = f't_{table}'
                # tableのデータを空にする
                _clear_data(db_file_path, table_name)

                # データを登録する
                elem: Union[list, dict] = config.get(db_file).get(table)
                if isinstance(elem, dict):
                    for (k, v) in elem.items():
                        _register_master_data(db_file_path, table_name, (k, v,))
                elif isinstance(elem, list):
                    for data in elem:
                        _register_master_data(db_file_path, table_name, (data, ))

    except Exception as err:
        print(f'ERROR: {err}')


def _clear_data(db_file_path: Path, table_name: str):
    try:
        with contextlib.closing(sqlite3.connect(db_file_path)) as conn:
            with conn as cur:
                cur.execute(f'DELETE FROM {table_name}')
    except Exception as err:
        print(f'ERROR: {err}')


def _register_master_data(db_file_path: Path, table_name: str, data: tuple[str, ...]):
    try:
        with contextlib.closing(sqlite3.connect(db_file_path)) as conn:
            with conn as cur:
                holders = ','.join(['?' for n in range(len(data))])
                cur.execute(f'INSERT INTO {table_name} VALUES ({holders})', data)
    except Exception as err:
        print(f'ERROR: {err}')


if __name__ == '__main__':
    parser = init_argparser()
    args = parser.parse_args()
    args.func(args)
