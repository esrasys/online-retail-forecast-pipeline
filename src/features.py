from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
MONTHLY_FILE = BASE_DIR / "data" / "processed" / "monthly_sales.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"
PLOT_FILE = OUTPUTS_DIR / "monthly_revenue_plot.png"


def load_monthly_data(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df["YearMonth"] = pd.to_datetime(df["YearMonth"], format="%Y-%m")
    df = df.sort_values("YearMonth").reset_index(drop=True)
    return df


def plot_monthly_revenue(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df["YearMonth"], df["MonthlyRevenue"], marker="o")
    plt.title("Monthly Revenue Over Time")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    df = load_monthly_data(MONTHLY_FILE)
    df = prepare_data(df)

    print("Monthly dataset preview:")
    print(df.head())
    print("\nDataset info:")
    print(df.dtypes)
    print(f"\nNumber of rows: {len(df)}")

    plot_monthly_revenue(df, PLOT_FILE)
    print(f"\nPlot saved to: {PLOT_FILE}")


if __name__ == "__main__":
    main()