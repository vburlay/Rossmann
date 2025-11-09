-- Создаём таблицы из исходных CSV

CREATE OR REPLACE TABLE raw_sales AS
SELECT
    Date ,
    Store,
    DayOfWeek,
    Sales,
    Customers,
    Open,
    Promo,
    StateHoliday,       -- ВАЖНО! текст
    SchoolHoliday
FROM read_csv_auto('data/raw/train.csv', types={
    'StateHoliday': 'VARCHAR'
});


CREATE OR REPLACE TABLE raw_store AS
SELECT
    Store,
    StoreType,
    Assortment,
    CompetitionDistance,
    CompetitionOpenSinceMonth,
    CompetitionOpenSinceYear,
    Promo2,
    Promo2SinceWeek,
    Promo2SinceYear,
    PromoInterval
FROM read_csv_auto('data/raw/store.csv'
    )
;

CREATE OR REPLACE TABLE raw_test AS
SELECT
    CAST(Date AS DATE) AS Date,
    Store,
    Open,
    Promo,
    StateHoliday,
    SchoolHoliday
FROM read_csv_auto('data/raw/test.csv'
    , types={
    'StateHoliday': 'VARCHAR'});
