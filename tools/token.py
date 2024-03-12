import argparse
import sqlite3
import contextlib
from pathlib import Path


def add(args):
    try:
        # get key/value from input.
        token_key = input('Token keyname:')
        token_value = input('Token string:')

        # Connect to database
        db_file_path = Path(args.database_filepath)
        with contextlib.closing(sqlite3.connect(db_file_path)) as conn:
            # create table(debug)
            with conn as cur:
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS t_token (\n'
                    'token_key TEXT PRIMARY KEY,\n'
                    'token_value TEXT\n'
                    ');'
                )

            # add
            with conn as cur:
                registered = cur.execute('SELECT COUNT(*) FROM t_token WHERE token_key=?', (token_key,)).fetchone()[0]
                if registered:
                    print(f'Key: {token_key} is already registered. exit.')
                    return
                cur.execute('INSERT INTO t_token VALUES (?, ?)', (token_key, token_value))

    except Exception as err:
        print(f'ERROR: {err}')


def update(args):
    try:
        # get key/value from input.
        token_key = input('Token keyname:')
        token_value = input('Token string:')

        # Connect to database
        db_file_path = Path(args.database_filepath)
        with contextlib.closing(sqlite3.connect(db_file_path)) as conn:
            # update
            with conn as cur:
                registered = cur.execute('SELECT COUNT(*) FROM t_token WHERE token_key=?', (token_key,)).fetchone()[0]
                if not registered:
                    print(f'Key: {token_key} is not registered. exit.')
                    return
                cur.execute('UPDATE t_token SET token_value=? WHERE token_key=?', (token_value, token_key))

    except Exception as err:
        print(f'ERROR: {err}')


def delete(args):
    try:
        # get key/value from input.
        token_key = input('Token keyname:')

        # Connect to database
        db_file_path = Path(args.database_filepath)
        with contextlib.closing(sqlite3.connect(db_file_path)) as conn:
            # delete
            with conn as cur:
                registered = cur.execute('SELECT COUNT(*) FROM t_token WHERE token_key=?', (token_key,)).fetchone()[0]
                if not registered:
                    print(f'Key: {token_key} is not registered. exit.')
                    return
                cur.execute('DELETE FROM t_token WHERE token_key=?', (token_key,))

    except Exception as err:
        print(f'ERROR: {err}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser('add', help='Add new token key/value pair.')
    parser_add.add_argument('database_filepath')
    parser_add.set_defaults(func=add)

    parser_update = subparsers.add_parser('update', help='Update token value.')
    parser_update.add_argument('database_filepath')
    parser_update.set_defaults(func=update)

    parser_delete = subparsers.add_parser('delete', help='Delete token key/value pair.')
    parser_delete.add_argument('database_filepath')
    parser_delete.set_defaults(func=delete)

    args = parser.parse_args()
    args.func(args)
