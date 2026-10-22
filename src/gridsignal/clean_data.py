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

PRICE_COLUMN = (
    "Germany/Luxembourg [€/MWh] Calculated resolutions"
)

TIMEZONE = "Europe/Berlin"


def main() -> None:
    df = pd.read_csv(RAW_FILE, sep=";", na_values=["-"])

    df["Start date"] = pd.to_datetime(
        df["Start date"],
        format="%b %d, %Y %I:%M %p",
        errors="raise",
    )

    df["End date"] = pd.to_datetime(
        df["End date"],
        format="%b %d, %Y %I:%M %p",
        errors="raise",
    )

    df[PRICE_COLUMN] = pd.to_numeric(
        df[PRICE_COLUMN],
        errors="coerce",
    )

    clean = df[
        ["Start date", "End date", PRICE_COLUMN]
    ].copy()

    clean = clean.rename(
        columns={
            "Start date": "start_time_local",
            "End date": "end_time_local",
            PRICE_COLUMN: "price_eur_mwh",
        }
    )

    clean = clean.dropna(
        subset=[
            "start_time_local",
            "end_time_local",
            "price_eur_mwh",
        ]
    )

    # Preserve the original order of repeated local timestamps.
    clean = clean.sort_values(
        "start_time_local",
        kind="stable",
    ).reset_index(drop=True)

    # Resolve repeated autumn hours using their chronological order.
    clean["start_time_berlin"] = (
        clean["start_time_local"].dt.tz_localize(
            TIMEZONE,
            ambiguous="infer",
            nonexistent="raise",
        )
    )

    # Convert each timestamp to an unambiguous UTC instant.
    clean["start_time_utc"] = (
        clean["start_time_berlin"].dt.tz_convert("UTC")
    )

    # Data-quality checks
    utc_diffs = clean["start_time_utc"].diff()
    duplicate_local = clean["start_time_local"].duplicated().sum()
    duplicate_utc = clean["start_time_utc"].duplicated().sum()

    print("\n--- Timestamp Quality Report ---")
    print(f"Rows: {len(clean):,}")
    print(f"Duplicate local timestamps: {duplicate_local}")
    print(f"Duplicate UTC timestamps: {duplicate_utc}")
    print(
        "UTC differences between consecutive records:"
    )
    print(utc_diffs.value_counts().sort_index().to_string())

    # Each record represents a one-hour market interval.
    interval_durations = (
        clean["end_time_local"] - clean["start_time_local"]
    )

    print("\n--- Interval Duration Check ---")
    print(
        interval_durations.value_counts()
        .sort_index()
        .to_string()
    )

    print("\n--- Price Quality Report ---")
    print(
        f"Missing prices: "
        f"{clean['price_eur_mwh'].isna().sum()}"
    )
    print(
        f"Negative-price intervals: "
        f"{(clean['price_eur_mwh'] < 0).sum()}"
    )
    print(
        f"Zero-price intervals: "
        f"{(clean['price_eur_mwh'] == 0).sum()}"
    )
    print(
        f"Minimum price: "
        f"{clean['price_eur_mwh'].min():.2f} €/MWh"
    )
    print(
        f"Maximum price: "
        f"{clean['price_eur_mwh'].max():.2f} €/MWh"
    )

    # Flag irregularities instead of silently deleting records.
    hourly_differences = utc_diffs.dropna()
    non_hourly_count = (
        hourly_differences != pd.Timedelta(hours=1)
    ).sum()

    if duplicate_utc > 0 or non_hourly_count > 0:
        print("\nWARNING: UTC timeline needs further investigation.")
        print(f"Non-hourly UTC differences: {non_hourly_count}")
    else:
        print("\nUTC timeline check passed.")

    # Keep useful columns in a consistent order.
    output_columns = [
        "start_time_local",
        "end_time_local",
        "start_time_utc",
        "price_eur_mwh",
    ]

    clean = clean[output_columns]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    clean.to_csv(OUTPUT_FILE, index=False)

    print(f"\nRows saved: {len(clean):,}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()