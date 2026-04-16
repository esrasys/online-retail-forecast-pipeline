from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
MONTHLY_FILE = BASE_DIR / "data" / "processed" / "monthly_sales.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"

PREDICTIONS_FILE = OUTPUTS_DIR / "baseline_predictions.csv"
METRICS_FILE = OUTPUTS_DIR / "model_metrics.csv"


def load_data(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["YearMonth"] = pd.to_datetime(df["YearMonth"], format="%Y-%m")
    df = df.sort_values("YearMonth").reset_index(drop=True)
    return df


def train_test_split_time_series(df: pd.DataFrame, test_size: int = 3):
    train = df.iloc[:-test_size].copy()
    test = df.iloc[-test_size:].copy()
    return train, test


def naive_forecast(train: pd.DataFrame, test: pd.DataFrame, target_col: str):
    last_value = train[target_col].iloc[-1]
    predictions = [last_value] * len(test)
    return predictions


def calculate_metrics(actual, predicted):
    actual = pd.Series(actual).reset_index(drop=True)
    predicted = pd.Series(predicted).reset_index(drop=True)

    mae = (actual - predicted).abs().mean()
    rmse = ((actual - predicted) ** 2).mean() ** 0.5
    mape = ((actual - predicted).abs() / actual).mean() * 100

    return {
        "Model": "Naive Forecast",
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
    }


def save_outputs(test: pd.DataFrame, predictions, metrics: dict):
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    results = test[["YearMonth", "MonthlyRevenue"]].copy()
    results["PredictedRevenue"] = predictions
    results.to_csv(PREDICTIONS_FILE, index=False)

    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(METRICS_FILE, index=False)


def main():
    df = load_data(MONTHLY_FILE)
    train, test = train_test_split_time_series(df, test_size=3)

    predictions = naive_forecast(train, test, "MonthlyRevenue")
    metrics = calculate_metrics(test["MonthlyRevenue"], predictions)

    print("Train period:")
    print(train[["YearMonth", "MonthlyRevenue"]])

    print("\nTest period:")
    print(test[["YearMonth", "MonthlyRevenue"]])

    print("\nPredictions:")
    print(predictions)

    print("\nMetrics:")
    print(metrics)

    save_outputs(test, predictions, metrics)

    print(f"\nPredictions saved to: {PREDICTIONS_FILE}")
    print(f"Metrics saved to: {METRICS_FILE}")


if __name__ == "__main__":
    main()