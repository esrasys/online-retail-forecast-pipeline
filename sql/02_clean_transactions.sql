DROP TABLE IF EXISTS transactions_clean;

CREATE TABLE transactions_clean AS
SELECT
    InvoiceNo,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,
    UnitPrice,
    CustomerID,
    Country,
    Quantity * UnitPrice AS Revenue
FROM transactions_raw
WHERE Quantity > 0
  AND UnitPrice > 0
  AND InvoiceDate IS NOT NULL;