from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "processed" / "online_retail.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"

RFM_FILE = OUTPUTS_DIR / "rfm_table.csv"
RFM_CLUSTERED_FILE = OUTPUTS_DIR / "rfm_clusters.csv"
RFM_SUMMARY_FILE = OUTPUTS_DIR / "rfm_cluster_summary.csv"
RFM_PLOT_FILE = OUTPUTS_DIR / "rfm_cluster_plot.png"


def load_data(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")

    df = df.dropna(subset=["CustomerID"])
    df["Description"] = df["Description"].fillna("Unknown Product")

    df = df.drop_duplicates().reset_index(drop=True)
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df


def build_rfm_table(df: pd.DataFrame) -> pd.DataFrame:
    reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()

    rfm["CustomerID"] = rfm["CustomerID"].astype(int)
    return rfm


def add_clusters(rfm: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    features = rfm[["Recency", "Frequency", "Monetary"]].copy()

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(scaled_features)

    return rfm


def build_cluster_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    summary = rfm.groupby("Cluster").agg(
        CustomerCount=("CustomerID", "count"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        AvgMonetary=("Monetary", "mean"),
    ).reset_index()

    summary["AvgRecency"] = summary["AvgRecency"].round(2)
    summary["AvgFrequency"] = summary["AvgFrequency"].round(2)
    summary["AvgMonetary"] = summary["AvgMonetary"].round(2)

    return summary.sort_values("Cluster").reset_index(drop=True)


def plot_clusters(rfm: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        rfm["Recency"],
        rfm["Monetary"],
        c=rfm["Cluster"],
        alpha=0.7
    )

    plt.title("Customer Segments Based on RFM")
    plt.xlabel("Recency")
    plt.ylabel("Monetary")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.colorbar(scatter, label="Cluster")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_outputs(rfm: pd.DataFrame, summary: pd.DataFrame) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    rfm.to_csv(RFM_FILE, index=False)
    rfm.to_csv(RFM_CLUSTERED_FILE, index=False)
    summary.to_csv(RFM_SUMMARY_FILE, index=False)


def main() -> None:
    print("Loading processed retail data...")
    df = load_data(RAW_FILE)

    print("Cleaning data for customer segmentation...")
    df = clean_data(df)

    print("Building RFM table...")
    rfm = build_rfm_table(df)

    print("Applying KMeans clustering...")
    rfm = add_clusters(rfm, n_clusters=4)

    summary = build_cluster_summary(rfm)

    print("\nRFM preview:")
    print(rfm.head())

    print(f"\nNumber of customers: {len(rfm)}")

    print("\nCluster summary:")
    print(summary)

    save_outputs(rfm, summary)
    plot_clusters(rfm, RFM_PLOT_FILE)

    print(f"\nRFM table saved to: {RFM_FILE}")
    print(f"Clustered RFM file saved to: {RFM_CLUSTERED_FILE}")
    print(f"Cluster summary saved to: {RFM_SUMMARY_FILE}")
    print(f"Cluster plot saved to: {RFM_PLOT_FILE}")


if __name__ == "__main__":
    main()