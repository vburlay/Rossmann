# Rossmann Store Sales Forecasting  
End-to-end forecasting system for Rossmann daily store sales using  
DuckDB, SQL feature engineering, XGBoost, FastAPI, and Dash.

![Made with Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-yellow)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange)
![Dash](https://img.shields.io/badge/Dash-Dashboard-lightgrey)

---

## 🚀 Overview

This repository implements a **complete production-style machine learning pipeline** for daily sales forecasting on the Rossmann dataset.  
The goal is to replicate how forecasting systems are built in real companies:

- analytical storage with DuckDB  
- SQL-based feature engineering  
- XGBoost regression model  
- offline batch prediction  
- FastAPI filtering endpoint  
- Dash interactive dashboard  

This project is designed not only as a solution, but as a **portfolio-level demonstration of full-stack ML engineering**.

---

## ✅ Highlights

### ✅ **Production-style architecture**
Full offline ETL → feature store → model → API → dashboard cycle.

### ✅ **Real-world time series feature engineering**
- calendar signals (dow, week, month, year)  
- lag features (1, 7, 30 days)  
- rolling windows (7, 30 days)  
- competition time difference  
- promo interval one-hot expansion  

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
│
├── dashboard/
│   └── app.py                   # Dash dashboard (AG Grid + FastAPI data)
│
├── config.py                    # central file paths (DB, model)
├── requirements.txt
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
## ✅ 6. Launch the Dash Dashboard
```bash
python dashboard/app.py
```
Dashboard includes:

✅ Store dropdown
✅ Date dropdown
✅ Dynamic API calls
✅ AG Grid data table

## 📊 Key Features Used in the Model

| Feature                                 | Description               |
| --------------------------------------- | ------------------------- |
| `lag1`, `lag7`, `lag30`                 | Previous days’ sales      |
| `avg7`, `avg30`                         | Rolling averages          |
| `dow`, `weeknum`, `monthnum`, `yearnum` | Calendar features         |
| `promo_*`                               | Promo interval indicators |
| `CompetitionDistance`                   | Store attribute           |
| `days_since_competition`                | Competition recency       |
| `StateHoliday`                          | Categorical holiday flags |

These features reflect actual retail forecasting logic.

## ✅ Technologies

| Component | Tool           |
| --------- | -------------- |
| Storage   | DuckDB         |
| ETL       | SQL, Python    |
| ML        | XGBoost        |
| Serve     | FastAPI        |
| UI        | Dash + AG Grid |
| Packaging | Pip            |

## ✅ Future Extensions
- Prophet / SARIMA baselines

- Feature importance analysis

- Hyperparameter optimization (Optuna)

- MLflow experiment tracking

- Docker deployment

- Airflow / Prefect pipeline

## ✅ Dataset

Kaggle competition:
https://www.kaggle.com/competitions/rossmann-store-sales

## 📜 License

MIT License.