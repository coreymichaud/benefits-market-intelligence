# TEMPORARY! This is just for testing for now.
import duckdb
from innovation_summit.config.paths import DB_PATH


with duckdb.connect(DB_PATH) as con:

    con.execute("CREATE SCHEMA IF NOT EXISTS gold")

    tables = con.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'silver'
        ORDER BY table_name
        """
    ).fetchall()

    for (table_name,) in tables:

        print(f"[COPYING] silver.{table_name} -> gold.{table_name}")

        con.execute(
            f"""
            CREATE OR REPLACE TABLE gold."{table_name}" AS
            SELECT *
            FROM silver."{table_name}"
            """
        )

print("[FINISHED] Gold schema successfully created!")