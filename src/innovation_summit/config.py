from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# DATA_PATH = PROJECT_ROOT / "data"
# RAW_DATA_PATH = DATA_PATH / "raw"
# COMBINED_DATA_PATH = DATA_PATH / "combined"
WAREHOUSE_PATH = PROJECT_ROOT / "data" / "warehouse"
DB_PATH = WAREHOUSE_PATH / "form_5500.db"
