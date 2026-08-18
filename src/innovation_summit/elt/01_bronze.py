import zipfile
import duckdb
import requests
from innovation_summit.config import WAREHOUSE_PATH, DB_PATH


files = {
    "F_5500": "Form 5500",
    "F_SCH_A": "Form 5500 Schedule A",
    "F_SCH_C_PART1_ITEM2": "Form 5500 Schedule C Part 1, Item 2",
}

WAREHOUSE_PATH.mkdir(parents=True, exist_ok=True)

# Connect and create DuckDB data warehouse, following B/S/G medallion architecture
with duckdb.connect(DB_PATH) as con:
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")

    for name, folder in files.items():
        print(f"[DOWNLOADING] {folder} from DOL EFAST...")

        for year in range(2019, 2025):
            stem = f"{name}_{year}_Latest"

            url = f"https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/{stem}.zip"

            zip_path = WAREHOUSE_PATH / f"{stem}.zip"

            print(f"  Downloading {year}...")

            response = requests.get(url)
            response.raise_for_status()
            zip_path.write_bytes(response.content)

            # Find the CSV inside the ZIP
            with zipfile.ZipFile(zip_path) as z:
                csv_files = [
                    file for file in z.namelist() if file.lower().endswith(".csv")
                ]

                csv_name = csv_files[0]

                # Extract only the CSV
                z.extract(csv_name, WAREHOUSE_PATH)

            csv_path = WAREHOUSE_PATH / csv_name

            # Use the ZIP filename as the DuckDB table name
            table_name = stem

            print(f"  Loading -> bronze.{table_name}")

            # Add data to bronze schema
            con.execute(
                f"""
                CREATE OR REPLACE TABLE bronze."{table_name}" AS
                SELECT *
                FROM read_csv_auto(
                    '{csv_path.as_posix()}',
                    header = true,
                    all_varchar = true
                )
                """
            )

            # Delete the temporary files
            csv_path.unlink()
            zip_path.unlink()

        print(f"[FINISHED] {folder}\n")
