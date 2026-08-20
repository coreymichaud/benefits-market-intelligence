import zipfile

import duckdb
import requests

from innovation_summit.config.paths import DB_PATH, RAW_DATA_PATH, WAREHOUSE_PATH


files = {
    "F_5500": "Form 5500",
    "F_SCH_A": "Form 5500 Schedule A",
    "F_SCH_C_PART1_ITEM2": "Form 5500 Schedule C Part 1, Item 2",
}

RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
WAREHOUSE_PATH.mkdir(parents=True, exist_ok=True)

# Connect to DuckDB data warehouse
with duckdb.connect(DB_PATH) as con:
    # Create bronze schema if it doesn't exist
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")

    for name, folder in files.items():
        folder_path = RAW_DATA_PATH / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        print(f"[DOWNLOADING] {folder} from DOL EFAST...")

        for year in range(2019, 2025):
            stem = f"{name}_{year}_Latest"

            url = f"https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/{stem}.zip"

            zip_path = folder_path / f"{stem}.zip"
            extract_path = folder_path / stem

            print(f"  Downloading {year}...")

            response = requests.get(url)
            response.raise_for_status()

            zip_path.write_bytes(response.content)

            with zipfile.ZipFile(zip_path) as z:
                csv_files = [
                    file for file in z.namelist() if file.lower().endswith(".csv")
                ]

                if not csv_files:
                    raise FileNotFoundError(f"No CSV found in {zip_path}")

                if len(csv_files) > 1:
                    raise ValueError(
                        f"Multiple CSV files found in {zip_path}: {csv_files}"
                    )

                csv_name = csv_files[0]

                # Create the year-specific folder
                extract_path.mkdir(parents=True, exist_ok=True)

                # Extract everything (CSV + layouts.txt, etc.) into the folder
                z.extractall(extract_path)

            csv_path = extract_path / csv_name

            table_name = stem

            print(f"  Loading -> bronze.{table_name}")

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

            zip_path.unlink()

        print(f"[FINISHED] {folder}\n")
