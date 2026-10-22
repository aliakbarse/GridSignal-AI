from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Day-ahead_prices_202312312100_202512312100_Hour.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "germany_day_ahead_prices_2024_2025.csv"
)

TIMEZONE = "Europe/Berlin"


def find_price_column(columns: list[str]) -> str:
    """Identify the Germany/Luxembourg day-ahead price column."""
    candidates = [
        column
        for column in columns
        if "Germany/Luxembourg" in column
        and "Calculated resolutions" in column
    ]

    if len(candidates) != 1:
        raise ValueError(
            "Could not uniquely identify the Germany/Luxembourg "
            f"price column. Matching columns: {candidates}. "
            f"Available columns: {list(columns)}"
        )

    return candidates[0]


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Raw price file not found: {RAW_FILE}")

    df = pd.read_csv(
        RAW_FILE,
        sep=";",
        na_values=["-"],
        encoding="utf-8-sig",
    )

    required_columns = {"Start date", "End date"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Raw file is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    price_column = find_price_column(list(df.columns))
    original_rows = len(df)

    df["Start date"] = pd.to_datetime(
        df["Start date"],
        format="%b %d, %Y %I:%M %p",
        errors="coerce",
    )
    df["End date"] = pd.to_datetime(
        df["End date"],
        format="%b %d, %Y %I:%M %p",
        errors="coerce",
    )
    df[price_column] = pd.to_numeric(
        df[price_column],
        errors="coerce",
    )

    clean = df[
        ["Start date", "End date", price_column]
    ].copy()

    clean = clean.rename(
        columns={
            "Start date": "start_time_local",
            "End date": "end_time_local",
            price_column: "price_eur_mwh",
        }
    )

    # Count missing or invalid values before dropping records.
    missing_start = int(clean["start_time_local"].isna().sum())
    missing_end = int(clean["end_time_local"].isna().sum())
    missing_price = int(clean["price_eur_mwh"].isna().sum())

    invalid_timestamps = (
        clean["start_time_local"].isna()
        | clean["end_time_local"].isna()
    )
    invalid_prices = clean["price_eur_mwh"].isna()
    rows_to_drop = invalid_timestamps | invalid_prices
    dropped_rows = int(rows_to_drop.sum())

    clean = clean.loc[~rows_to_drop].copy()

    if clean.empty:
        raise ValueError("No valid price records remain after cleaning.")

    # Preserve source order for repeated local timestamps during
    # the autumn daylight-saving transition.
    clean = clean.sort_values(
        "start_time_local",
        kind="stable",
    ).reset_index(drop=True)

    clean["start_time_berlin"] = (
        clean["start_time_local"].dt.tz_localize(
            TIMEZONE,
            ambiguous="infer",
            nonexistent="raise",
        )
    )
    clean["start_time_utc"] = (
        clean["start_time_berlin"].dt.tz_convert("UTC")
    )

    # Check timestamp uniqueness and hourly continuity.
    utc_diffs = clean["start_time_utc"].diff()
    duplicate_local = int(
        clean["start_time_local"].duplicated().sum()
    )
    duplicate_utc = int(
        clean["start_time_utc"].duplicated().sum()
    )
    non_hourly_count = int(
        (
            utc_diffs.dropna()
            != pd.Timedelta(hours=1)
        ).sum()
    )

    interval_durations = (
        clean["end_time_local"] - clean["start_time_local"]
    )

    print("\n--- Cleaning Summary ---")
    print(f"Input rows: {original_rows:,}")
    print(f"Rows retained: {len(clean):,}")
    print(f"Rows dropped: {dropped_rows:,}")
    print(f"Rows with missing/invalid start times: {missing_start:,}")
    print(f"Rows with missing/invalid end times: {missing_end:,}")
    print(f"Rows with missing/invalid prices: {missing_price:,}")

    print("\n--- Timestamp Quality Report ---")
    print(f"Duplicate local timestamps: {duplicate_local}")
    print(f"Duplicate UTC timestamps: {duplicate_utc}")
    print(f"Non-hourly UTC gaps: {non_hourly_count}")
    print("\nUTC differences between consecutive records:")
    print(utc_diffs.value_counts().sort_index().to_string())

    print("\n--- Interval Duration Check ---")
    print(interval_durations.value_counts().sort_index().to_string())

    print("\n--- Price Quality Report ---")
    print(
        f"Negative-price intervals: "
        f"{(clean['price_eur_mwh'] < 0).sum():,}"
    )
    print(
        f"Zero-price intervals: "
        f"{(clean['price_eur_mwh'] == 0).sum():,}"
    )
    print(
        f"Minimum price: {clean['price_eur_mwh'].min():.2f} EUR/MWh"
    )
    print(
        f"Maximum price: {clean['price_eur_mwh'].max():.2f} EUR/MWh"
    )

    if duplicate_utc > 0 or non_hourly_count > 0:
        print(
            "\nWARNING: Duplicate UTC timestamps or irregular "
            "hourly gaps require investigation."
        )
    else:
        print("\nUTC timeline check passed.")

    output_columns = [
        "start_time_local",
        "end_time_local",
        "start_time_utc",
        "price_eur_mwh",
    ]
    clean = clean[output_columns]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(OUTPUT_FILE, index=False)

    print(f"\nRows saved: {len(clean):,}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()