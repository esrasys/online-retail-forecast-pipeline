from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "processed" / "online_retail.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"

DAILY_SALES_FILE = OUTPUTS_DIR / "daily_sales.csv"
DAILY_PLOT_FILE = OUTPUTS_DIR / "daily_sales_plot.png"
ROLLING_PLOT_FILE = OUTPUTS_DIR / "daily_sales_rolling_plot.png"
TS_PREDICTIONS_FILE = OUTPUTS_DIR / "timeseries_predictions.csv"
TS_METRICS_FILE = OUTPUTS_DIR / "timeseries_model_metrics.csv"
TS_FORECAST_PLOT_FILE = OUTPUTS_DIR / "timeseries_forecast_vs_actual.png"


def load_data(file_path: Path) -> pd.DataFrame:
    return pd.read_csv(file_path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df


def build_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    daily_sales = (
        df.groupby(df["InvoiceDate"].dt.date)["Revenue"]
        .sum()
        .reset_index()
    )
    daily_sales.columns = ["Date", "DailyRevenue"]
    daily_sales["Date"] = pd.to_datetime(daily_sales["Date"])
    daily_sales = daily_sales.sort_values("Date").reset_index(drop=True)
    return daily_sales


def add_rolling_average(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    df = df.copy()
    df["RollingAvg7"] = df["DailyRevenue"].rolling(window=window).mean()
    return df


def plot_daily_sales(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 5))
    plt.plot(df["Date"], df["DailyRevenue"])
    plt.title("Daily Revenue Over Time")
    plt.xlabel("Date")
    plt.ylabel("Daily Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_rolling_average(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 5))
    plt.plot(df["Date"], df["DailyRevenue"], label="Daily Revenue")
    plt.plot(df["Date"], df["RollingAvg7"], label="7-Day Rolling Average")
    plt.title("Daily Revenue with 7-Day Rolling Average")
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def train_test_split_time_series(df: pd.DataFrame, test_size: int = 30):
    train = df.iloc[:-test_size].copy()
    test = df.iloc[-test_size:].copy()
    return train, test


def naive_forecast(train: pd.DataFrame, test: pd.DataFrame) -> list:
    last_value = float(train["DailyRevenue"].iloc[-1])
    return [last_value] * len(test)


def moving_average_forecast(train: pd.DataFrame, test: pd.DataFrame, window: int = 7) -> list:
    history = train["DailyRevenue"].tolist()
    predictions = []

    for _ in range(len(test)):
        if len(history) >= window:
            pred = sum(history[-window:]) / window
        else:
            pred = sum(history) / len(history)
        predictions.append(float(pred))
        history.append(pred)

    return predictions


def calculate_metrics(actual, predicted, model_name: str) -> dict:
    actual = pd.Series(actual).reset_index(drop=True)
    predicted = pd.Series(predicted).reset_index(drop=True)

    mae = float((actual - predicted).abs().mean())
    rmse = float((((actual - predicted) ** 2).mean()) ** 0.5)
    mape = float(((actual - predicted).abs() / actual).mean() * 100)

    return {
        "Model": model_name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
    }


def save_predictions(test: pd.DataFrame, naive_preds: list, ma_preds: list, output_path: Path) -> None:
    results = test[["Date", "DailyRevenue"]].copy()
    results["NaiveForecast"] = naive_preds
    results["MovingAverageForecast"] = ma_preds
    results.to_csv(output_path, index=False)


def save_metrics(metrics_list: list, output_path: Path) -> None:
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv(output_path, index=False)


def plot_forecasts(train: pd.DataFrame, test: pd.DataFrame, naive_preds: list, ma_preds: list, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 5))
    plt.plot(train["Date"], train["DailyRevenue"], label="Train Actual")
    plt.plot(test["Date"], test["DailyRevenue"], label="Test Actual")
    plt.plot(test["Date"], naive_preds, label="Naive Forecast")
    plt.plot(test["Date"], ma_preds, label="Moving Average Forecast")

    plt.title("Daily Revenue Forecast vs Actual")
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    print("Loading processed retail data...")
    df = load_data(RAW_FILE)

    print("Cleaning data for time series analysis...")
    df = clean_data(df)

    print("Building daily sales series...")
    daily_sales = build_daily_sales(df)
    daily_sales = add_rolling_average(daily_sales, window=7)

    print("\nDaily sales preview:")
    print(daily_sales.head())

    print(f"\nNumber of daily observations: {len(daily_sales)}")
    print(f"Date range: {daily_sales['Date'].min()} to {daily_sales['Date'].max()}")

    train, test = train_test_split_time_series(daily_sales, test_size=30)

    naive_preds = naive_forecast(train, test)
    ma_preds = moving_average_forecast(train, test, window=7)

    naive_metrics = calculate_metrics(test["DailyRevenue"], naive_preds, "Naive Forecast")
    ma_metrics = calculate_metrics(test["DailyRevenue"], ma_preds, "7-Day Moving Average")

    print("\nModel metrics:")
    print(naive_metrics)
    print(ma_metrics)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    daily_sales.to_csv(DAILY_SALES_FILE, index=False)
    save_predictions(test, naive_preds, ma_preds, TS_PREDICTIONS_FILE)
    save_metrics([naive_metrics, ma_metrics], TS_METRICS_FILE)

    plot_daily_sales(daily_sales, DAILY_PLOT_FILE)
    plot_rolling_average(daily_sales, ROLLING_PLOT_FILE)
    plot_forecasts(train, test, naive_preds, ma_preds, TS_FORECAST_PLOT_FILE)

    print(f"\nDaily sales saved to: {DAILY_SALES_FILE}")
    print(f"Daily sales plot saved to: {DAILY_PLOT_FILE}")
    print(f"Rolling average plot saved to: {ROLLING_PLOT_FILE}")
    print(f"Predictions saved to: {TS_PREDICTIONS_FILE}")
    print(f"Metrics saved to: {TS_METRICS_FILE}")
    print(f"Forecast plot saved to: {TS_FORECAST_PLOT_FILE}")


if __name__ == "__main__":
    main()