import sqlite3
from pathlib import Path
import sys
from typing import Final


def create_table_main(database_file_path: Path):
    cities = ['niigata', 'nagaoka',]

    conn: Final[sqlite3.Connection] = sqlite3.connect(database_file_path)
    cursor: Final[sqlite3.Cursor] = conn.cursor()

    for city_name in cities:
        cursor.execute(
            f'CREATE TABLE IF NOT EXISTS t_disaster_text_{city_name} (\n'
            'id INTEGER PRIMARY KEY AUTOINCREMENT,\n'
            'datetime TIMESTAMP NOT NULL,\n'
            'disaster_text TEXT NOT NULL\n,'
            ');'
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    try:
        db_file_path = Path()  # TODO: implement
        create_table_main(db_file_path)

    except Exception as err:
        print(f'create_table.py FAILED: {err}')
        sys.exit(1)  # 失敗

    sys.exit(0)  # 成功
