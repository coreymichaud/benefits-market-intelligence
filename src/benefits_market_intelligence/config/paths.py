from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = PROJECT_ROOT / "data"

RAW_DATA_PATH = DATA_PATH / "raw"
PROCESSED_PATH = DATA_PATH / "processed"
DB_PATH = PROCESSED_PATH / "form_5500.duckdb"
EXPORTS_PATH = DATA_PATH / "exports"
