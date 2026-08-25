from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROCESSED_PATH / "form_5500.duckdb"
