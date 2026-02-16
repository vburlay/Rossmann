import duckdb
import joblib
import numpy as np

from config import DB_PATH, BASE_DIR
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error

# =========================
# Load data
# =========================
con = duckdb.connect(DB_PATH)
df = con.sql("SELECT * FROM features WHERE Sales IS NOT NULL").df()

# =========================
# Cast categoricals (BEFORE split)
# =========================
cat_cols = ["StateHoliday", "StoreType", "Assortment"]
for c in cat_cols:
    df[c] = df[c].astype("category")

# =========================
# Time-based split
# =========================
split_date = "2015-06-01"

train = df[df["Date"] < split_date]
val   = df[df["Date"] >= split_date]

# =========================
# Feature selection
# =========================
drop_cols = ["Sales", "Date", "comp_start_date", "PromoInterval"]
feature_cols = [c for c in df.columns if c not in drop_cols]

# sanity check
bad = train[feature_cols].select_dtypes(
    exclude=["number", "bool", "category"]
).columns.tolist()
assert not bad, f"Неподдерживаемые типы в признаках: {bad}"

# =========================
# Model
# =========================
model = XGBRegressor(
    n_estimators=600,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    enable_categorical=True,
    tree_method="hist",
    random_state=42
)

# =========================
# Train ONLY on past
# =========================
model.fit(
    train[feature_cols],
    train["Sales"]
)

# =========================
# Validate ONLY on future
# =========================
val_pred = model.predict(val[feature_cols])
mae = mean_absolute_error(val["Sales"], val_pred)

print(f"Validation MAE: {mae:,.2f}")
#Validation MAE: 403.84

#Baseline
naive = val.groupby("Store")["Sales"].shift(7) #strong baseline
mae_naive = mean_absolute_error(val["Sales"][~naive.isna()], naive.dropna())
print(mae_naive)
#Naive (lag-7) MAE ≈ 2480

#Median Absolute Percentage Error (Median APE)
#Oбычный MAPE: взрывается при малых продажах, чувствителен к выбросам
#median APE: устойчив к аномалиям отражает «типичное» качество прогноза
print((np.abs(val["Sales"] - val_pred) / val["Sales"]).median())
#Median Absolute Percentage Error (Median APE) = 0.0479  ≈ 4.8%
# =========================
# Save model
# =========================
joblib.dump(model, BASE_DIR / "model/store_sales_xgb.pkl")
print("✅ Model saved")
