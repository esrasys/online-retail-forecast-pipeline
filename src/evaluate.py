from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
MONTHLY_FILE = BASE_DIR / "data" / "processed" / "monthly_sales.csv"
PREDICTIONS_FILE = BASE_DIR / "outputs" / "baseline_predictions.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"
EVAL_PLOT_FILE = OUTPUTS_DIR / "forecast_vs_actual.png"


def load_monthly_data(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["YearMonth"] = pd.to_datetime(df["YearMonth"], format="%Y-%m")
    df = df.sort_values("YearMonth").reset_index(drop=True)
    return df


def load_predictions(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["YearMonth"] = pd.to_datetime(df["YearMonth"])
    return df


def plot_forecast_vs_actual(monthly_df: pd.DataFrame, pred_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    test_months = pred_df["YearMonth"]
    train_df = monthly_df[~monthly_df["YearMonth"].isin(test_months)].copy()
    test_df = monthly_df[monthly_df["YearMonth"].isin(test_months)].copy()

    plt.figure(figsize=(10, 5))
    plt.plot(train_df["YearMonth"], train_df["MonthlyRevenue"], marker="o", label="Train Actual")
    plt.plot(test_df["YearMonth"], test_df["MonthlyRevenue"], marker="o", label="Test Actual")
    plt.plot(pred_df["YearMonth"], pred_df["PredictedRevenue"], marker="o", label="Baseline Forecast")

    plt.title("Actual vs Baseline Forecast")
    plt.xlabel("Month")
    plt.ylabel("Monthly Revenue")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    monthly_df = load_monthly_data(MONTHLY_FILE)
    pred_df = load_predictions(PREDICTIONS_FILE)

    print("Predictions preview:")
    print(pred_df)

    plot_forecast_vs_actual(monthly_df, pred_df, EVAL_PLOT_FILE)
    print(f"\nEvaluation plot saved to: {EVAL_PLOT_FILE}")


if __name__ == "__main__":
    main()