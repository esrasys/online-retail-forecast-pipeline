from pathlib import Path
import sqlite3
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "raw" / "Online Retail.xlsx"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_FILE = BASE_DIR / "data" / "retail.db"
CSV_FILE = PROCESSED_DIR / "online_retail.csv"

SQL_DIR = BASE_DIR / "sql"
SQL_SCRIPTS = [
    SQL_DIR / "01_check_raw_data.sql",
    SQL_DIR / "02_clean_transactions.sql",
    SQL_DIR / "03_monthly_aggregation.sql",
]


def load_excel(file_path: Path) -> pd.DataFrame:
    """Load the Excel file into a pandas DataFrame."""
    df = pd.read_excel(file_path)
    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Save raw data as CSV for easier inspection and reuse."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def load_to_sqlite(df: pd.DataFrame, db_path: Path, table_name: str = "transactions_raw") -> None:
    """Load DataFrame into a SQLite database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)


def run_sql_script(conn: sqlite3.Connection, script_path: Path) -> None:
    """Run a SQL script from file."""
    print(f"Running SQL script: {script_path.name}")
    sql = script_path.read_text(encoding="utf-8")
    conn.executescript(sql)


def export_monthly_sales(db_path: Path, output_path: Path) -> None:
    """Export the monthly_sales table to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        df_monthly = pd.read_sql_query(
            "SELECT * FROM monthly_sales ORDER BY YearMonth;",
            conn
        )

    df_monthly.to_csv(output_path, index=False)
    print(f"Monthly sales exported to: {output_path}")


def main() -> None:
    print("Reading Excel file...")
    df = load_excel(RAW_FILE)

    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    print("Column names:")
    print(df.columns.tolist())

    print("Saving CSV copy...")
    save_csv(df, CSV_FILE)

    print("Loading data into SQLite...")
    load_to_sqlite(df, DB_FILE)

    with sqlite3.connect(DB_FILE) as conn:
        for script in SQL_SCRIPTS:
            run_sql_script(conn, script)

    export_monthly_sales(DB_FILE, PROCESSED_DIR / "monthly_sales.csv")

    print("Done.")
    print(f"Raw CSV saved to: {CSV_FILE}")
    print(f"SQLite database saved to: {DB_FILE}")


if __name__ == "__main__":
    main()