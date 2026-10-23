
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/germany_market_combined_2024_2025.csv")
MIN_NEGATIVE_HOURS = 30

REQUIRED_COLUMNS = [
    "start_time_utc",
    "price_eur_mwh",
    "solar_mwh",
    "wind_onshore_mwh",
    "wind_offshore_mwh",
]

GENERATION_COLUMNS = [
    "solar_mwh",
    "wind_onshore_mwh",
    "wind_offshore_mwh",
]


def analyze_monthly_generation(data: pd.DataFrame) -> pd.DataFrame:
    """Compare monthly generation during negative and nonnegative price hours."""

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    df = data[REQUIRED_COLUMNS].copy()

    df["start_time_utc"] = pd.to_datetime(
        df["start_time_utc"],
        utc=True,
        errors="coerce",
    )

    numeric_columns = ["price_eur_mwh", *GENERATION_COLUMNS]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError(
            "Input contains missing or invalid timestamps or numeric values."
        )

    # Derive the calendar year and month in German local time.
    local_time = df["start_time_utc"].dt.tz_convert("Europe/Berlin")
    df["year"] = local_time.dt.year
    df["month"] = local_time.dt.month

    # Restrict the analysis to 2024 and 2025.
    df = df[df["year"].isin([2024, 2025])].copy()

    if df.empty:
        raise ValueError("No observations found for 2024 or 2025.")

    df["price_category"] = (
        df["price_eur_mwh"]
        .lt(0)
        .map({
            True: "Negative price",
            False: "Nonnegative price",
        })
    )

    # Calculate the number of observed hours and average generation.
    grouped = (
        df.groupby(
            ["year", "month", "price_category"],
            observed=True,
        )
        .agg(
            observed_hours=("price_eur_mwh", "size"),
            average_solar_mwh=("solar_mwh", "mean"),
            average_wind_onshore_mwh=("wind_onshore_mwh", "mean"),
            average_wind_offshore_mwh=("wind_offshore_mwh", "mean"),
        )
    )

    # Keep both price categories for every month, including months
    # with zero negative-price hours.
    expected_index = pd.MultiIndex.from_product(
        [
            [2024, 2025],
            range(1, 13),
            ["Negative price", "Nonnegative price"],
        ],
        names=["year", "month", "price_category"],
    )

    results = grouped.reindex(expected_index).reset_index()

    results["observed_hours"] = (
        results["observed_hours"].fillna(0).astype(int)
    )

    # Count negative-price hours by BOTH year and month.
    # This avoids the previous incorrect year-only mapping.
    negative_counts = (
        df.assign(is_negative=df["price_eur_mwh"].lt(0))
        .groupby(["year", "month"], as_index=False)
        .agg(negative_price_hours=("is_negative", "sum"))
    )

    results = results.merge(
        negative_counts,
        on=["year", "month"],
        how="left",
        validate="many_to_one",
    )

    results["negative_price_hours"] = (
        results["negative_price_hours"].fillna(0).astype(int)
    )

    # Flag months where negative-price observations are limited.
    def classify_sample(hours: int) -> str:
        if hours == 0:
            return "No negative-price hours"
        if hours < MIN_NEGATIVE_HOURS:
            return "Small sample — interpret cautiously"
        return "At least 30 negative-price hours"

    results["sample_status"] = results["negative_price_hours"].map(
        classify_sample
    )

    # Calculate generation differences:
    # negative-price average minus nonnegative-price average.
    generation_averages = results.pivot(
        index=["year", "month"],
        columns="price_category",
        values=[
            "average_solar_mwh",
            "average_wind_onshore_mwh",
            "average_wind_offshore_mwh",
        ],
    )

    comparisons = pd.DataFrame(index=generation_averages.index)

    for column in GENERATION_COLUMNS:
        average_column = f"average_{column}"

        negative_average = generation_averages[
            (average_column, "Negative price")
        ]
        nonnegative_average = generation_averages[
            (average_column, "Nonnegative price")
        ]

        difference_column = f"{column}_difference_mwh"
        percentage_column = f"{column}_difference_pct"

        comparisons[difference_column] = (
            negative_average - nonnegative_average
        )

        comparisons[percentage_column] = (
            comparisons[difference_column]
            .div(nonnegative_average.where(nonnegative_average.ne(0)))
            .mul(100)
        )

    comparisons = comparisons.reset_index()

    results = results.merge(
        comparisons,
        on=["year", "month"],
        how="left",
        validate="many_to_one",
    )

    results = results.sort_values(
        ["year", "month", "price_category"]
    ).reset_index(drop=True)

    return results


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}\n"
            "Run the data-cleaning and combining pipeline first."
        )

    data = pd.read_csv(INPUT_FILE)
    results = analyze_monthly_generation(data)

    print("\nMonthly renewable generation by price category")
    print(
        "Generation averages and absolute differences: "
        "MWh per observed hour."
    )
    print(
        "Percentage differences use nonnegative-price averages as baseline."
    )
    print(
        f"Small-sample threshold: fewer than "
        f"{MIN_NEGATIVE_HOURS} negative-price hours."
    )
    print(
        "\nNote: Generation differences are repeated for both price "
        "categories within each month."
    )

    columns_to_display = [
        "year",
        "month",
        "price_category",
        "observed_hours",
        "negative_price_hours",
        "sample_status",
        "average_solar_mwh",
        "solar_mwh_difference_mwh",
        "solar_mwh_difference_pct",
        "average_wind_onshore_mwh",
        "wind_onshore_mwh_difference_mwh",
        "wind_onshore_mwh_difference_pct",
        "average_wind_offshore_mwh",
        "wind_offshore_mwh_difference_mwh",
        "wind_offshore_mwh_difference_pct",
    ]

    print(
        results[columns_to_display].to_string(
            index=False,
            na_rep="N/A",
            float_format=lambda value: f"{value:,.1f}",
        )
    )


if __name__ == "__main__":
    main()
