# WIP! Not here quite yet. The code below is just to see table names.

import duckdb

from innovation_summit.config import DB_PATH


with duckdb.connect(DB_PATH, read_only=True) as con:
    for schema in ["bronze", "silver"]:
        print(f"\n{schema}")
        print("-" * len(schema))

        tables = con.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = ?
            ORDER BY table_name
            """,
            [schema],
        ).fetchall()

        for (table,) in tables:
            print(f"  {table}")
