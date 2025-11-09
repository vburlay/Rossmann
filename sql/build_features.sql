-- ================================================================
--  FEATURES SQL FOR ROSSMANN STORES SALES
--  Combines cleaned sales with store metadata.
--  Adds calendar, competition, promo, lag and rolling window features.
--  This is the recommended full version (Kuhn-style engineering).
-- ================================================================

CREATE OR REPLACE TABLE features AS

-- ------------------------------------------------
-- 1. Base join: combine sales + store attributes
-- ------------------------------------------------
WITH base AS (
    SELECT
        s.Date,
        s.Store,
        s.Sales,
        s.Customers,
        s.Promo,
        s.StateHoliday,
        s.SchoolHoliday,

        -- store metadata
        st.StoreType,
        st.Assortment,
        st.CompetitionDistance,
        st.CompetitionOpenSinceMonth,
        st.CompetitionOpenSinceYear,
        st.Promo2,
        st.Promo2SinceWeek,
        st.Promo2SinceYear,
        st.PromoInterval,

        -- calendar features
        EXTRACT(DAYOFWEEK FROM s.Date) AS dow,
        EXTRACT(WEEK FROM s.Date) AS weeknum,
        EXTRACT(MONTH FROM s.Date) AS monthnum,
        EXTRACT(YEAR FROM s.Date) AS yearnum

    FROM cleaned_sales s
    LEFT JOIN raw_store st ON s.Store = st.Store
),

-- ------------------------------------------------
-- 2. Handle missing store metadata (Kuhn ch.8)
-- ------------------------------------------------
clean AS (
    SELECT
        *,
        CASE
            WHEN CompetitionDistance IS NULL THEN 0
            ELSE CompetitionDistance
        END AS CompetitionDistance_fe,

        CASE
            WHEN CompetitionOpenSinceYear IS NULL THEN NULL
            ELSE MAKE_DATE(
                CompetitionOpenSinceYear,
                COALESCE(CompetitionOpenSinceMonth, 1),
                1
            )
        END AS comp_start_date
    FROM base
),

-- ------------------------------------------------
-- 3. Competition time difference
-- ------------------------------------------------
comp AS (
    SELECT
        *,
        CASE
            WHEN comp_start_date IS NULL THEN 0
            ELSE DATE_DIFF('day', comp_start_date, Date)
        END AS days_since_competition
    FROM clean
),

-- ------------------------------------------------
-- 4. Numeric feature engineering: lag + rolling
--    (Kuhn ch.6, essential for retail forecasting)
-- ------------------------------------------------
lags AS (
    SELECT
        *,
        -- Lags
        LAG(Sales, 1) OVER (PARTITION BY Store ORDER BY Date) AS lag1,
        LAG(Sales, 7) OVER (PARTITION BY Store ORDER BY Date) AS lag7,
        LAG(Sales, 30) OVER (PARTITION BY Store ORDER BY Date) AS lag30,

        -- Rolling means
        AVG(Sales) OVER (
            PARTITION BY Store
            ORDER BY Date
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS avg7,

        AVG(Sales) OVER (
            PARTITION BY Store
            ORDER BY Date
            ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING
        ) AS avg30
    FROM comp
),

-- ------------------------------------------------
-- 5. PromoInterval engineering (categorical → binary)
-- ------------------------------------------------
promo_int AS (
    SELECT
        *,
        CASE WHEN PromoInterval LIKE '%Jan%' THEN 1 ELSE 0 END AS promo_jan,
        CASE WHEN PromoInterval LIKE '%Feb%' THEN 1 ELSE 0 END AS promo_feb,
        CASE WHEN PromoInterval LIKE '%Mar%' THEN 1 ELSE 0 END AS promo_mar,
        CASE WHEN PromoInterval LIKE '%Apr%' THEN 1 ELSE 0 END AS promo_apr,
        CASE WHEN PromoInterval LIKE '%May%' THEN 1 ELSE 0 END AS promo_may,
        CASE WHEN PromoInterval LIKE '%Jun%' THEN 1 ELSE 0 END AS promo_jun,
        CASE WHEN PromoInterval LIKE '%Jul%' THEN 1 ELSE 0 END AS promo_jul,
        CASE WHEN PromoInterval LIKE '%Aug%' THEN 1 ELSE 0 END AS promo_aug,
        CASE WHEN PromoInterval LIKE '%Sep%' THEN 1 ELSE 0 END AS promo_sep,
        CASE WHEN PromoInterval LIKE '%Oct%' THEN 1 ELSE 0 END AS promo_oct,
        CASE WHEN PromoInterval LIKE '%Nov%' THEN 1 ELSE 0 END AS promo_nov,
        CASE WHEN PromoInterval LIKE '%Dec%' THEN 1 ELSE 0 END AS promo_dec
    FROM lags
)

-- ------------------------------------------------
-- FINAL RESULT
-- ------------------------------------------------
SELECT
    * EXCLUDE PromoInterval     -- remove raw string column (breaks XGB)
FROM promo_int;
