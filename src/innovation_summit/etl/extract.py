import requests
import zipfile
from pathlib import Path
from innovation_summit.config import RAW_DATA_PATH

files = {
    "F_5500": ("Form 5500", range(2019, 2025)),
    "F_SCH_A": ("Form 5500 Schedule A", range(2019, 2025)),
    "F_SCH_C_PART1_ITEM2": ("Form 5500 Schedule C Part 1, Item 2", range(2019, 2026)),
}

for name, (folder, years) in files.items():
    folder_path = RAW_DATA_PATH / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    print(f"[DOWNLOADING] {folder} from DOL EFAST...")

    for year in years:
        stem = f"{name}_{year}_Latest"
        url = f"https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/{stem}.zip"

        zip_path = folder_path / f"{stem}.zip"
        extract_path = folder_path / stem

        zip_path.write_bytes(requests.get(url).content)

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_path)

        zip_path.unlink()

    print(f"[FINISHED] {folder} raw data successfully downloaded!\n")