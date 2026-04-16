DROP TABLE IF EXISTS monthly_sales;

CREATE TABLE monthly_sales AS
SELECT
    substr(InvoiceDate, 1, 7) AS YearMonth,
    ROUND(SUM(Revenue), 2) AS MonthlyRevenue,
    COUNT(DISTINCT InvoiceNo) AS OrderCount,
    COUNT(DISTINCT CustomerID) AS UniqueCustomers
FROM transactions_clean
GROUP BY substr(InvoiceDate, 1, 7)
ORDER BY YearMonth;