# Rossmann Store Sales Forecasting  
End-to-end forecasting system for Rossmann daily store sales using  
DuckDB, SQL feature engineering, XGBoost, FastAPI, and Dash.

![Made with Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-yellow)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange)
![Dash](https://img.shields.io/badge/Dash-Dashboard-lightgrey)

---

## 🚀 Project Overview

This repository implements an **end-to-end forecasting pipeline** for daily retail store sales using the Rossmann Kaggle dataset.

The goal is not only to train a model, but to demonstrate how a real forecasting system is built in production:

- **Analytical storage layer:** DuckDB  
- **Feature engineering in SQL:** reproducible and fast  
- **Modeling layer:** baseline → XGBoost regression  
- **Offline batch scoring:** predictions are precomputed and stored  
- **Serving layer:** FastAPI (read-only)  
- **UI layer:** Dash dashboard with AG Grid filtering  

This project is designed as a **portfolio-grade ML engineering system**, with a clean separation between
data preparation, modeling, serving, and dashboard delivery.

---

## ✅ Highlights

### ✅ **Production-style architecture**
Full offline ETL → feature store → model → API → dashboard cycle.

### ✅ Time series feature engineering (SQL-first)
EDA confirms strong weekly seasonality and promotional effects, so the feature pipeline includes:

- calendar signals (`dow`, `weeknum`, `monthnum`, `yearnum`)  
- lag features (`lag1`, `lag7`, `lag30`)  
- rolling windows (`avg7`, `avg30`)  
- promo and holiday signals  
- competition recency features  
- PromoInterval expansion into monthly flags  

### ✅ **Modern, efficient data backend**
DuckDB outperforms pandas for analytical queries and allows all transformations in pure SQL.

### ✅ **Deployable API**
FastAPI returns prediction slices by `store` and `date`, ready for dashboards or web apps.

### ✅ **Professional dashboard**
Dash + AG Grid provides instant filtering and clean UI.

Recruiters immediately see: you understand **ML, data engineering, API development, and UI delivery**.

---

## 🧱 Architecture

                                   ┌──────── Kaggle CSVs ────────┐
                 │  data/raw/train|test|store  │
                 └────────────┬────────────────┘
                              │  (SQL ETL)
                      db/sql/*.sql  → DuckDB
                              │
                  ┌───────────▼───────────┐
                  │   db/warehouse.duckdb │
                  │  raw_* → cleaned_* →  │
                  │        features       │
                  └───────────┬───────────┘
                              │
                     (train_model.py)
                              │
               ┌──────────────▼──────────────┐
               │   model/store_sales_xgb.pkl │
               └──────────────┬──────────────┘
                              │
                    (predict_all.py) writes
                              │
                      ┌───────▼────────┐
                      │  predictions   │  ← DuckDB table
                      └───────┬────────┘
     /filter?store=…&date=…   │
         FastAPI JSON         │
            ┌─────────────────▼──────────────────┐
            │             Dash UI                │
            │    Dropdowns → call FastAPI        │
            │    Show AG Grid with predictions   │
            └────────────────────────────────────┘

---

## 📦 Repository Structure
```text
Rossmann/
│
├── data/
│   └── raw/                     # original Kaggle CSVs (train.csv, test.csv, store.csv)
│
├── db/
│   ├── warehouse.duckdb         # main DuckDB database (auto-created)
│   ├── build_database.py        # ETL runner (executes SQL scripts)
│   └── sql/
│       ├── load_raw.sql         # load raw CSV files
│       ├── clean_data.sql       # cleaning and formatting
│       ├── cleaned_sales.sql    # join and normalize sales data
│       └── build_features.sql   # feature engineering pipeline
│
├── model/
│   ├── train_model.py           # trains XGBoost model
│   ├── predict_all.py           # writes batch predictions → DuckDB table `predictions`
│   └── store_sales_xgb.pkl      # trained model
│
├── api/
│   └── fastapi_app.py           # REST API: /filter?store=&date=
├── notebooks/
│   └── rossmann_eda.ipynb       # REST EDA
│
├── dashboard/
│   └── app.py                   # Dash dashboard (AG Grid + FastAPI data)
│
├── config.py                    # central file paths (DB, model)
├── requirements.txt
├── EDA_summary.md
└── README.md
```
## ✅ 1. Installation
Clone the repository:

```bash
git clone https://github.com/vburlay/rossmann-forecasting.git
cd rossmann-forecasting
pip install -r requirements.txt

```

## ✅ 2. Build the DuckDB database

```bash
python db/build_database.py
```
Creates:

- raw_sales, raw_store, raw_test

- cleaned dataset

- fully engineered features table

## ✅ 3. Train the model
```bash
python model/train_model.py

```
This produces:

- trained XGBoost regressor (hist tree method)

- saved model in /model/store_sales_xgb.pkl

## ✅ 4. Generate batch predictions

```bash
python model/predict_all.py
```

Outputs:

- predictions table with all features + final forecast

## ✅ 5. Start FastAPI

```bash
uvicorn api.fastapi_app:app --reload

```
Example:

```bash
GET /filter?store=1&date=2015-07-01

```
Response:
```bash
[
  {
    "Store": 1,
    "Date": "2015-07-01",
    "prediction": 5084,
    "Customers": 562,
    "lag7": 3762,
    "avg30": 4422.13,
    "Promo": 1
  }
]


```
## ✅ 6. Start the Dashboard (Dash + AG Grid)
```bash
python dashboard/app.py
```
Dashboard includes:

✅ Store dropdown filter
✅ Date dropdown filter
✅ Automatic FastAPI calls (no page reload)
✅ AG Grid interactive table

## 📌 Feature Contract (Model Input)

This project follows a Feature Contract approach: the forecasting model expects a fixed set of engineered features.

The contract is derived from EDA findings and is designed to be:

- leakage-safe (history-only time features)

- store-aware (all lags/rollings computed per store)

- production-friendly (reproducible SQL pipeline in DuckDB)

✅ Target Variable

Sales — daily store sales (prediction target)

Note: During inference, predictions should be forced to 0 when Open == 0.
1) Entity Keys (required)

| Column  | Type    | Notes                                         |
| ------- | ------- | --------------------------------------------- |
| `Store` | INTEGER | Store identifier (panel time series key)      |
| `Date`  | DATE    | Time index (must be sorted within each store) |

2) Calendar Features (seasonality signals)

EDA confirmed strong weekly and calendar-driven seasonality, so these features are mandatory:

| Feature    | Type    | Description     |
| ---------- | ------- | --------------- |
| `dow`      | INTEGER | Day of week     |
| `weeknum`  | INTEGER | ISO week number |
| `monthnum` | INTEGER | Month number    |
| `yearnum`  | INTEGER | Year            |

Optional (if used):

| Feature      | Type          | Description  |
| ------------ | ------------- | ------------ |
| `is_weekend` | INTEGER (0/1) | Weekend flag |
| `dayofyear`  | INTEGER       | Day of year  |

3) Business Driver Features (exogenous signals)

EDA showed that promotions and store attributes explain a large part of variance.

| Feature         | Type               | Description                             |
| --------------- | ------------------ | --------------------------------------- |
| `Open`          | INTEGER (0/1)      | Store open flag                         |
| `Promo`         | INTEGER (0/1)      | Main promo indicator (strong predictor) |
| `StateHoliday`  | VARCHAR / CATEGORY | Holiday type (`0`, `a`, `b`, `c`)       |
| `SchoolHoliday` | INTEGER (0/1)      | School holiday indicator                |

4) Store Metadata (static / slow-moving)

These features capture store heterogeneity observed in EDA.

| Feature                     | Type               | Description              |
| --------------------------- | ------------------ | ------------------------ |
| `StoreType`                 | VARCHAR / CATEGORY | Store type               |
| `Assortment`                | VARCHAR / CATEGORY | Assortment type          |
| `CompetitionDistance`       | DOUBLE             | Distance to competitor   |
| `CompetitionOpenSinceMonth` | INTEGER            | Competition open month   |
| `CompetitionOpenSinceYear`  | INTEGER            | Competition open year    |
| `Promo2`                    | INTEGER (0/1)      | Store enrolled in Promo2 |
| `Promo2SinceWeek`           | INTEGER            | Promo2 start week        |
| `Promo2SinceYear`           | INTEGER            | Promo2 start year        |

5) Competition Recency Feature

Competition metadata is converted into a time-dependent signal.

| Feature                  | Type    | Description                                      |
| ------------------------ | ------- | ------------------------------------------------ |
| `days_since_competition` | INTEGER | Days since competition start date (0 if unknown) |

6) PromoInterval Expansion (monthly flags)

PromoInterval is expanded into 12 binary indicators:

promo_jan ... promo_dec

| Feature   | Type          | Description                   |
| --------- | ------------- | ----------------------------- |
| `promo_*` | INTEGER (0/1) | Promo scheduled in that month |

7) Lag Features (store-level memory)

EDA (ACF/PACF + store-level inspection) supports strong weekly dependencies.

✅ All lag features must be computed per store:

| Feature | Type   | Description     |
| ------- | ------ | --------------- |
| `lag1`  | DOUBLE | Sales at `t-1`  |
| `lag7`  | DOUBLE | Sales at `t-7`  |
| `lag30` | DOUBLE | Sales at `t-30` |

8) Rolling Window Features (history-only baselines)

✅ Rolling windows must not include the current day.

| Feature | Type   | Description                                    |
| ------- | ------ | ---------------------------------------------- |
| `avg7`  | DOUBLE | Mean Sales over last 7 days (excluding today)  |
| `avg30` | DOUBLE | Mean Sales over last 30 days (excluding today) |

Leakage-safe SQL pattern:

`AVG(Sales) OVER (
  PARTITION BY Store
  ORDER BY Date
  ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING
) AS avg30`

🚫 Leakage Rules (critical)

Forbidden features

| Column      | Reason                                                         |
| ----------- | -------------------------------------------------------------- |
| `Customers` | Not available in Kaggle test data + strong target leakage risk |

### Validation rule

**Always use time-based split (no random shuffle split)**


## ✅ Tech Stack

| Layer               | Tool           |
| ------------------- | -------------- |
| Storage             | DuckDB         |
| Feature Engineering | SQL            |
| Modeling            | XGBoost        |
| Batch Scoring       | Python         |
| Serving             | FastAPI        |
| Dashboard           | Dash + AG Grid |


## ✅ Future Extensions

- Classical baselines (Seasonal Naive, ETS, ARIMA)

- Feature importance analysis (SHAP)

- Hyperparameter tuning (Optuna)

- Experiment tracking (MLflow)

- Docker / Docker Compose deployment

- Workflow orchestration (Prefect / Airflow)

## ✅ Dataset

Kaggle competition:
https://www.kaggle.com/competitions/rossmann-store-sales

## 📜 License

MIT License.