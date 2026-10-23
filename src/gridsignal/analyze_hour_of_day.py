
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/germany_market_combined_2024_2025.csv")
OUTPUT_DIR = Path("docs")

REQUIRED_COLUMNS = {
    "start_time_local",
    "price_eur_mwh",
    "solar_mwh",
    "year",
    "month",
}

# Meteorological seasons
SEASON_MONTHS = {
    "Winter": [12, 1, 2],
    "Spring": [3, 4, 5],
    "Summer": [6, 7, 8],
    "Autumn": [9, 10, 11],
}

SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]


def load_data() -> pd.DataFrame:
    """Load the dataset, validate columns, and derive analysis fields."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}\n"
            "Run this script from the project root directory."
        )

    data = pd.read_csv(INPUT_FILE)

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Parse timestamps with mixed UTC offsets, then convert to German
    # local time. This correctly handles CET and CEST.
    data["start_time_local"] = pd.to_datetime(
        data["start_time_local"],
        format="mixed",
        errors="coerce",
        utc=True,
    ).dt.tz_convert("Europe/Berlin")

    data["price_eur_mwh"] = pd.to_numeric(
        data["price_eur_mwh"], errors="coerce"
    )
    data["solar_mwh"] = pd.to_numeric(
        data["solar_mwh"], errors="coerce"
    )

    original_rows = len(data)

    data = data.dropna(
        subset=[
            "start_time_local",
            "price_eur_mwh",
            "solar_mwh",
        ]
    ).copy()

    dropped_rows = original_rows - len(data)

    # Derive the hour and month using German local time.
    data["hour"] = data["start_time_local"].dt.hour
    data["month"] = data["start_time_local"].dt.month

    # Negative means strictly below zero. A price of exactly zero
    # belongs to the nonnegative category.
    data["is_negative_price"] = data["price_eur_mwh"] < 0

    data["price_category"] = data["is_negative_price"].map(
        {
            True: "Negative price",
            False: "Nonnegative price",
        }
    )

    month_to_season = {
        month: season
        for season, months in SEASON_MONTHS.items()
        for month in months
    }
    data["season"] = data["month"].map(month_to_season)

    print(f"Loaded {len(data):,} valid hourly records.")
    print(f"Rows excluded due to invalid values: {dropped_rows:,}")
    print(f"Years covered: {sorted(data['year'].unique().tolist())}")

    return data


def analyze_hourly_frequency(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate negative-price frequency by local hour and year.

    The rate uses the actual observed records in each hour as its
    denominator, rather than assuming every hour has equal coverage.
    """
    summary = (
        data.groupby(["year", "hour"], as_index=False)
        .agg(
            observed_hours=("is_negative_price", "size"),
            negative_price_hours=("is_negative_price", "sum"),
        )
    )

    summary["negative_price_rate_pct"] = (
        summary["negative_price_hours"]
        / summary["observed_hours"]
        * 100
    )

    return summary.sort_values(["year", "hour"]).reset_index(drop=True)


def analyze_solar_by_hour(data: pd.DataFrame) -> pd.DataFrame:
    """
    Compare solar generation during negative and nonnegative prices
    for each local hour and year.
    """
    summary = (
        data.groupby(
            ["year", "hour", "price_category"],
            as_index=False,
            observed=True,
        )
        .agg(
            observed_hours=("solar_mwh", "size"),
            average_solar_mwh=("solar_mwh", "mean"),
            median_solar_mwh=("solar_mwh", "median"),
        )
    )

    return summary.sort_values(
        ["year", "hour", "price_category"]
    ).reset_index(drop=True)


def analyze_seasons(data: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize prices and solar generation by season and price category.
    """
    summary = (
        data.groupby(
            ["year", "season", "price_category"],
            as_index=False,
            observed=True,
        )
        .agg(
            observed_hours=("price_eur_mwh", "size"),
            average_price_eur_mwh=("price_eur_mwh", "mean"),
            average_solar_mwh=("solar_mwh", "mean"),
        )
    )

    summary["season"] = pd.Categorical(
        summary["season"],
        categories=SEASON_ORDER,
        ordered=True,
    )

    return summary.sort_values(
        ["year", "season", "price_category"]
    ).reset_index(drop=True)


def print_hourly_frequency(summary: pd.DataFrame) -> None:
    """Print the hourly negative-price results in a readable format."""
    print("\nNEGATIVE-PRICE FREQUENCY BY GERMAN LOCAL HOUR")
    print("Rate = negative-price hours / observed hours")

    display = summary.copy()
    display["negative_price_rate_pct"] = (
        display["negative_price_rate_pct"].map(
            lambda value: f"{value:.2f}%"
        )
    )

    print(display.to_string(index=False))

    print("\nHighest negative-price rates by year:")
    for year in sorted(summary["year"].unique()):
        year_data = summary[summary["year"] == year]
        highest = year_data.loc[
            year_data["negative_price_rate_pct"].idxmax()
        ]

        print(
            f"{year}: {int(highest['hour']):02d}:00 — "
            f"{highest['negative_price_rate_pct']:.2f}% "
            f"({int(highest['negative_price_hours'])} negative-price "
            f"hours out of {int(highest['observed_hours'])} observed)"
        )


def print_seasonal_summary(summary: pd.DataFrame) -> None:
    """Print seasonal averages by year and price category."""
    print("\nSEASONAL PRICE AND SOLAR SUMMARY")

    display = summary.copy()
    display["average_price_eur_mwh"] = (
        display["average_price_eur_mwh"].map(
            lambda value: f"{value:.2f}"
        )
    )
    display["average_solar_mwh"] = (
        display["average_solar_mwh"].map(
            lambda value: f"{value:,.2f}"
        )
    )

    print(display.to_string(index=False))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = load_data()

    hourly_frequency = analyze_hourly_frequency(data)
    solar_by_hour = analyze_solar_by_hour(data)
    seasonal_summary = analyze_seasons(data)

    outputs = {
        "hourly_negative_price_frequency_2024_2025.csv":
            hourly_frequency,
        "hourly_solar_by_price_category_2024_2025.csv":
            solar_by_hour,
        "seasonal_price_and_solar_summary_2024_2025.csv":
            seasonal_summary,
    }

    for filename, result in outputs.items():
        output_path = OUTPUT_DIR / filename
        result.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

    print_hourly_frequency(hourly_frequency)
    print_seasonal_summary(seasonal_summary)

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()
