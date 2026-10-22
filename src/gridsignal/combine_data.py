
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TIMEZONE = "Europe/Berlin"

PRICE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "germany_day_ahead_prices_2024_2025.csv"
)
GENERATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "germany_generation_2024_2025.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "germany_market_combined_2024_2025.csv"
)


def main() -> None:
    prices = pd.read_csv(PRICE_FILE)
    generation = pd.read_csv(GENERATION_FILE)

    prices["start_time_utc"] = pd.to_datetime(
        prices["start_time_utc"],
        utc=True,
        errors="raise",
    )
    generation["start_time_utc"] = pd.to_datetime(
        generation["start_time_utc"],
        utc=True,
        errors="raise",
    )

    # Filter by German local calendar year, not UTC year.
    prices["start_time_local"] = (
        prices["start_time_utc"].dt.tz_convert(TIMEZONE)
    )
    generation["start_time_local"] = (
        generation["start_time_utc"].dt.tz_convert(TIMEZONE)
    )

    prices = prices[
        prices["start_time_local"].dt.year.isin([2024, 2025])
    ].copy()
    generation = generation[
        generation["start_time_local"].dt.year.isin([2024, 2025])
    ].copy()

    if prices["start_time_utc"].duplicated().any():
        raise ValueError("Duplicate UTC timestamps found in price data.")

    if generation["start_time_utc"].duplicated().any():
        raise ValueError(
            "Duplicate UTC timestamps found in generation data."
        )

    generation_columns = [
        "start_time_utc",
        "wind_offshore_mwh",
        "wind_onshore_mwh",
        "wind_total_mwh",
        "solar_mwh",
        "renewables_selected_mwh",
    ]

    combined = prices.merge(
        generation[generation_columns],
        on="start_time_utc",
        how="outer",
        indicator=True,
        validate="one_to_one",
    )

    print("\n--- Dataset Join Report ---")
    print(f"Price records: {len(prices):,}")
    print(f"Generation records: {len(generation):,}")
    print(f"Combined records: {len(combined):,}")
    print("\nTimestamp match status:")
    print(combined["_merge"].value_counts().to_string())

    unmatched = combined["_merge"] != "both"
    if unmatched.any():
        raise ValueError(
            "Some timestamps did not match. Review the join report "
            "before continuing."
        )

    combined = combined.drop(columns="_merge")

    combined["start_time_local"] = (
        combined["start_time_utc"].dt.tz_convert(TIMEZONE)
    )
    combined["year"] = combined["start_time_local"].dt.year
    combined["month"] = combined["start_time_local"].dt.month
    combined["is_negative_price"] = (
        combined["price_eur_mwh"] < 0
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    print("\n--- Records by German Local Year ---")
    print(combined.groupby("year").size().to_string())

    print(f"\nSaved combined data to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
