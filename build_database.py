import duckdb
from config import DB_PATH
# DB einschließen
con = duckdb.connect(DB_PATH)

# SQL-List um auszuführen
sql_files = [
    "sql/load_raw.sql",
    "sql/clean_data.sql",
    "sql/cleaned_sales.sql",
    "sql/build_features.sql",
]
for sql_file in sql_files:
    print(f"📌 Executing {sql_file} ...")
    with open(sql_file) as f:
        con.execute(f.read())
print("✅ Database built successfully!")