CREATE OR REPLACE TABLE cleaned_sales AS
SELECT
    s.Store,
    s.Date,
    s.Sales,
    s.Customers,
    s.Open,
    s.Promo,
    s.StateHoliday,
    s.SchoolHoliday
FROM raw_sales s
WHERE s.Open = 1 AND s.Sales > 0;
