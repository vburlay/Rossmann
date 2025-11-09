import duckdb
import joblib

from config import DB_PATH, BASE_DIR
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error

con = duckdb.connect(DB_PATH)
df = con.sql("SELECT * FROM features WHERE Sales IS NOT NULL").df()

# какие колонки категоризовать
cat_cols = ["StateHoliday", "StoreType", "Assortment"]  # PromoInterval опустим
for c in cat_cols:
    df[c] = df[c].astype("category")

# какие колонки исключить из признаков
drop_cols = ["Sales", "Date", "comp_start_date", "PromoInterval"]  # datetime и raw object убираем
feature_cols = [c for c in df.columns if c not in drop_cols]

# контроль: убедимся, что нет object/datetime
bad = df[feature_cols].select_dtypes(exclude=["number", "bool", "category"]).columns.tolist()
assert not bad, f"Неподдерживаемые типы в признаках: {bad}"

model = XGBRegressor(
    n_estimators=600,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    enable_categorical=True,
    tree_method="hist"
)

model.fit(df[feature_cols], df["Sales"])
pred = model.predict(df[feature_cols])

print("MAE:", mean_absolute_error(df["Sales"], pred))

joblib.dump(model, BASE_DIR / "model/store_sales_xgb.pkl")
print("✅ Model saved")
