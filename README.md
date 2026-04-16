# Online Retail Forecast Pipeline

An end-to-end Python + SQL forecasting project built on transaction-level online retail data.

## Project Goal

The goal of this project is to transform raw e-commerce transaction data into a monthly forecasting dataset and build a simple baseline revenue forecast workflow.

This project demonstrates:
- raw data ingestion from Excel
- loading data into SQLite
- SQL-based cleaning and monthly aggregation
- Python-based time series preparation
- baseline forecasting
- model evaluation and visualization

## Dataset

This project uses the **Online Retail** dataset containing transaction-level sales records with the following columns:

- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

The forecasting target is:

- **MonthlyRevenue**

Additional monthly indicators:
- **OrderCount**
- **UniqueCustomers**

## Project Structure

```text
online-retail-forecast-pipeline/
├── data/
│   ├── raw/
│   │   └── Online Retail.xlsx
│   ├── processed/
│   │   ├── online_retail.csv
│   │   └── monthly_sales.csv
│   └── retail.db
├── outputs/
│   ├── baseline_predictions.csv
│   ├── forecast_vs_actual.png
│   ├── model_metrics.csv
│   └── monthly_revenue_plot.png
├── sql/
│   ├── 01_check_raw_data.sql
│   ├── 02_clean_transactions.sql
│   └── 03_monthly_aggregation.sql
├── src/
│   ├── evaluate.py
│   ├── extract.py
│   ├── features.py
│   └── train.py
└── requirements.txt