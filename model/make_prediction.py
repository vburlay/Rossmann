import duckdb, joblib
from config import DB_PATH, BASE_DIR

con = duckdb.connect(DB_PATH)
model = joblib.load(BASE_DIR / "model/store_sales_xgb.pkl")

df = con.sql("SELECT * FROM features").df()

df["StateHoliday"] = df["StateHoliday"].astype("category")
df["StoreType"] = df["StoreType"].astype("category")
df["Assortment"] = df["Assortment"].astype("category")

feature_cols = [c for c in df.columns if c not in ("Sales", "Date")]

df["prediction"] = model.predict(df[feature_cols]).round().astype(int)

con.execute("DROP TABLE IF EXISTS predictions")
con.execute("CREATE TABLE predictions AS SELECT * FROM df")

print("✅ Predictions saved")

