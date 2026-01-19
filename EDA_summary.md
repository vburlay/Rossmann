<!-- File: EDA_summary.md -->

# Rossmann Sales Forecasting — EDA Summary

## Purpose
This EDA investigates the Rossmann sales dataset to understand demand dynamics and to identify **leakage-safe** signals that can be engineered into features for forecasting (target: `Sales`, commonly modeled as `log1p(Sales)`).

---

## Data Sources and Join Logic
- **Tables:** `raw_sales` (transactional daily store data) and `raw_store` (store metadata).
- **Join:** left merge on `Store` to enrich sales records with store attributes.

---

## Data Quality and Preprocessing
### Type casting
- Converted `Date` to datetime.
- Converted categorical fields to `category`:
  - `StoreType`, `Assortment`, `StateHoliday`.

### Sorting (critical for time features)
- Sorted by `["Store", "Date"]` and reset index.
- This is mandatory for any **lag/rolling/diff** transformations.

### Missing values: diagnostics and treatment
- Visualized missingness using heatmaps and `missingno` plots.
- Imputation rules (consistent with modeling requirements):
  - `CompetitionOpenSinceYear/Month` → `0` (unknown/not available; enables masking later).
  - `Promo2SinceYear/Week` → `0` (not enrolled or unknown start).
  - `CompetitionDistance` → `max_distance * 2` (avoid treating missing as “near competitor”).
  - `PromoInterval` → `"None"` (no scheduled Promo2 interval).

### PromoInterval parsing
- Converted `PromoInterval` into monthly binary flags: `Promo_Jan … Promo_Dec`.
- Dropped original text column to improve model compatibility.

---

## Target Distribution and Variance Stabilization
### Observations
- `Sales` and `Customers` are strongly right-skewed with large outliers (expected due to store heterogeneity).

### Transformation
- Created `Sales_log = log1p(Sales)` to:
  - reduce skewness,
  - stabilize variance,
  - improve learnability for models (especially tree-based).

### Diagnostics
- Histograms (with KDE) and QQ-plots show improved distribution shape after log transform (not necessarily normal, but less heavy-tailed).

---

## Time-Series Structure (Global and Store Level)
### Global series construction
- Built daily aggregated series:
  - `daily = log1p(sum(Sales by Date))`.
- Used this to inspect macro dynamics and detect seasonality.

### Calendar patterns (global)
- Clear weekly structure via:
  - `DayOfWeek` aggregation,
  - day-of-week bar/box plots.
- Month-level effects were explored using monthly averages.

---

## Business Drivers
Visual analyses indicate meaningful demand shifts associated with:
- **Promo:** large uplift in sales distribution during promo periods.
- **StoreType / Assortment:** strong between-group differences (store heterogeneity).
- **Promo2:** additional effect when active (requires correct “active” logic during modeling).
- **StateHoliday:** heterogeneous impact by holiday type.
- **CompetitionDistance:** weak-to-moderate relationship; more useful as a baseline modifier than a primary driver.

---

## Temporal Dependence Diagnostics
### ACF (autocorrelation)
- Computed ACF for:
  - selected stores (store-level daily aggregated series),
  - global daily series (`daily`).
- Peaks in ACF highlight candidate seasonal lags (weekly-like structure expected around 7, 14, 28).

### PACF (partial autocorrelation)
- PACF computed for a selected store using `log1p(Sales)` (store-level, `Open == 1`).
- PACF is used as a diagnostic for direct lag effects after accounting for intermediate lags; it is a heuristic for candidate lag features.

### Interpretation note
ACF/PACF results guide **candidate** lag horizons but **do not guarantee** performance gains. Final selection must be validated with time-based CV.

---

## Smoothing and Decomposition
### Rolling mean
- 30-day rolling mean applied to global series to reduce noise and reveal slower components.

### STL decomposition
- STL with weekly period (7) decomposes global series into:
  - trend,
  - seasonal,
  - residual components.
- Confirms deterministic weekly seasonality typical for retail.

### Promo activity vs sales
- Compared smoothed sales to daily promo share (fraction of stores on promo) to qualitatively assess co-movement.

---

## Stationarity Checks (Store Level)
### Setup
- Built store-level daily series for a chosen `store_id`, filtered to `Open == 1`.

### Tests
- **ADF (null: unit root / non-stationary)**
- **KPSS (null: stationary)**

### Compared series views
- Level: `Sales`
- Log level: `log1p(Sales)`
- Differenced log: `diff(log1p(Sales))`

### Key takeaway
The log-transformed store-level series can reject unit root under ADF while still showing strong deterministic weekly seasonality. Trend/unit-root and seasonality are separate phenomena.

---

## Modeling-Oriented Feature Preview (Leakage-Safe)
### Calendar features
- `year`, `week`, `day`, `dayofyear`, `is_weekend`.

### Cyclical encodings
- `sin_week`, `cos_week`, `sin_month`, `cos_month`.

### Lag features (per store)
- `sales_log_lag_{1,7,14,28}` via `groupby("Store").shift(lag)`.

### Rolling features (per store, history-only)
- `sales_roll_7`, `sales_roll_30` computed as:
  - `shift(1).rolling(window).mean()` to avoid leakage.

### Competition and promo features
- `competition_open_months` (masked when open date missing).
- `log_competition_distance = log1p(CompetitionDistance)`.
- Promo2 active logic should be computed using ISO year/week during modeling.

### Missing values created by lags/rolling
- Filled lag/rolling NaNs with robust statistics (median) to preserve early observations in each store history.

---

## Key Findings
- Strong and consistent **weekly seasonality** across stores.
- **Promo** is a major sales driver.
- High store heterogeneity: `StoreType` and `Assortment` matter.
- Competition effects are weaker but potentially useful in combination with other predictors.
- Autocorrelation supports the use of **lag and rolling statistics** as predictive features.

---

## Implications for Modeling
- Use **time-based validation** (walk-forward or blocked CV), not random splits.
- Ensure all engineered features are computed from **past-only** information (`shift(1)` for rolling).
- During inference/evaluation, enforce business rule:
  - if `Open == 0`, predicted sales should be `0`.
- Prefer store-aware models (store id + store history features) such as XGBoost with carefully constructed lags/rolling.

---

## Next Steps
Proceed to the modeling notebook:
1. Time-based split + walk-forward CV.
2. Baseline model (e.g., XGBoost) using leakage-safe features.
3. Evaluate via CV, tune features, and confirm gains from lag/rolling horizons.
4. Build submission pipeline with `Open == 0 → 0` post-processing.
