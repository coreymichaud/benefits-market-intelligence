from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
WAREHOUSE_PATH = PROJECT_ROOT / "data" / "warehouse"
DB_PATH = WAREHOUSE_PATH / "form_5500.db"