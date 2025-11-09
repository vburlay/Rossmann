CREATE OR REPLACE TABLE cleaned_sales AS
SELECT
    Date,
    Store,
    Sales,
    Customers,
    Open,
    Promo,
    StateHoliday,
    SchoolHoliday
FROM raw_sales
WHERE Open = 1 AND Sales > 0;
