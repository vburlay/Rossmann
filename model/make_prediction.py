# predict_to_db.py

import duckdb, joblib
from config import DB_PATH, MODEL_PATH

con = duckdb.connect(DB_PATH)

# Load model
model = joblib.load(MODEL_PATH)

# Load full features WITH Date
full_df = con.sql("SELECT * FROM features").df()

# Save keys for table output
date_col = full_df["Date"]
store_col = full_df["Store"]

# Prepare df for XGBoost
df = full_df.copy()

# Categorical columns
cat_cols = ["StateHoliday", "StoreType", "Assortment"]
for c in cat_cols:
    if c in df.columns:
        df[c] = df[c].fillna("Unknown").astype("category")

# Remove unsupported columns
drop_cols = ["Sales", "Date", "comp_start_date"]
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# Predict
pred = model.predict(df).round().astype(int)

# Build predictions table
result = df.copy()
result["prediction"] = pred
result["Date"] = date_col
result["Store"] = store_col
result["Date"] = result["Date"].astype(str)
# Save
con.execute("DROP TABLE IF EXISTS predictions")
con.execute("CREATE TABLE predictions AS SELECT * FROM result")

con.close()
print("✅ predictions table created")



