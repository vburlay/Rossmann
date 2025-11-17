from pathlib import Path

# Корень проекта Rossmann
BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
# Путь к базе
DB_PATH = BASE_DIR / "db" / "warehouse.duckdb"

# Путь к модели
MODEL_PATH = BASE_DIR / "model" / "store_sales_xgb.pkl"
