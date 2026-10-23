
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "germany_market_combined_2024_2025.csv"
)

REQUIRED_COLUMNS = [
    "start_time_utc",
    "price_eur_mwh",
    "solar_mwh",
    "wind_onshore_mwh",
    "wind_offshore_mwh",
    "wind_total_mwh",
]

GENERATION_COLUMNS = [
    "solar_mwh",
    "wind_onshore_mwh",
    "wind_offshore_mwh",
    "wind_total_mwh",
]


def analyze_generation_by_price(data: pd.DataFrame) -> pd.DataFrame:
    """Compare average renewable generation across price categories."""
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    df = data.copy()

    df["start_time_utc"] = pd.to_datetime(
        df["start_time_utc"], utc=True, errors="raise"
    )

    numeric_columns = ["price_eur_mwh", *GENERATION_COLUMNS]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if df[["start_time_utc", *numeric_columns]].isna().any().any():
        raise ValueError("Required timestamps and numeric values cannot be missing.")

    df["year"] = (
        df["start_time_utc"]
        .dt.tz_convert("Europe/Berlin")
        .dt.year
    )

    df = df[df["year"].isin([2024, 2025])].copy()

    df["price_category"] = df["price_eur_mwh"].map(
        lambda price: (
            "Negative price" if price < 0 else "Nonnegative price"
        )
    )

    results = (
        df.groupby(["year", "price_category"], observed=True)
        .agg(
            observed_hours=("price_eur_mwh", "size"),
            average_solar_mwh=("solar_mwh", "mean"),
            average_onshore_wind_mwh=("wind_onshore_mwh", "mean"),
            average_offshore_wind_mwh=("wind_offshore_mwh", "mean"),
            average_total_wind_mwh=("wind_total_mwh", "mean"),
        )
        .reset_index()
        .sort_values(["year", "price_category"])
        .reset_index(drop=True)
    )

    return results


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Combined dataset not found: {DATA_PATH}\n"
            "Run the data pipeline before this analysis."
        )

    data = pd.read_csv(DATA_PATH)
    results = analyze_generation_by_price(data)

    display_columns = [
        "year",
        "price_category",
        "observed_hours",
        "average_solar_mwh",
        "average_onshore_wind_mwh",
        "average_offshore_wind_mwh",
        "average_total_wind_mwh",
    ]

    print("\nRenewable generation by electricity-price category")
    print("Generation values are averages per observed hour, in MWh.\n")
    print(results[display_columns].to_string(
        index=False,
        formatters={
            column: "{:,.2f}".format
            for column in GENERATION_COLUMNS
            if column in results.columns
        },
    ))


if __name__ == "__main__":
    main()
