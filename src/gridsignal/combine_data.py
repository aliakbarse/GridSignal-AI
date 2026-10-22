from pathlib import Path

import pandas as pd

from gridsignal.data_validation import combine_market_data

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

    # Convert timestamps to UTC before filtering by German local year.
    for df in [prices, generation]:
        df["start_time_utc"] = pd.to_datetime(
            df["start_time_utc"],
            utc=True,
            errors="raise",
        )

        df["start_time_local"] = (
            df["start_time_utc"].dt.tz_convert(TIMEZONE)
        )

    prices = prices[
        prices["start_time_local"].dt.year.isin([2024, 2025])
    ].copy()

    generation = generation[
        generation["start_time_local"].dt.year.isin([2024, 2025])
    ].copy()

    combined = combine_market_data(prices, generation)

    print("\n--- Dataset Join Report ---")
    print(f"Price records: {len(prices):,}")
    print(f"Generation records: {len(generation):,}")
    print(f"Combined records: {len(combined):,}")

    print("\n--- Records by German Local Year ---")
    print(combined.groupby("year").size().to_string())

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved combined data to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()