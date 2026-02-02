import duckdb
from config import DB_PATH, SQL_PATH

sql_files = [
    SQL_PATH / "load_raw.sql",
    SQL_PATH / "cleaned_sales.sql",
    SQL_PATH / "build_features.sql",
]

with duckdb.connect(str(DB_PATH)) as con:
    for sql_file in sql_files:
        print(f"📌 Executing {sql_file} ...")
        with open(sql_file, "r", encoding="utf-8") as f:
            con.execute(f.read())

print("✅ Database built successfully!")