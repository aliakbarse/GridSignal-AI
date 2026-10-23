
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/germany_market_combined_2024_2025.csv")
OUTPUT_FILE = Path("docs/monthly_solar_consistency_2024_2025.csv")

MIN_NEGATIVE_HOURS = 30

REQUIRED_COLUMNS = [
    "start_time_utc",
    "price_eur_mwh",
    "solar_mwh",
]


def analyze_solar_consistency(data: pd.DataFrame) -> pd.DataFrame:
    """Compare monthly solar averages by electricity price category."""

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    df = data[REQUIRED_COLUMNS].copy()

    df["start_time_utc"] = pd.to_datetime(
        df["start_time_utc"],
        utc=True,
        errors="coerce",
    )

    for column in ["price_eur_mwh", "solar_mwh"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError(
            "The input contains missing or invalid timestamps or values."
        )

    local_time = df["start_time_utc"].dt.tz_convert("Europe/Berlin")
    df["year"] = local_time.dt.year
    df["month"] = local_time.dt.month

    df = df[df["year"].isin([2024, 2025])].copy()

    df["is_negative_price"] = df["price_eur_mwh"] < 0

    monthly = (
        df.groupby(
            ["year", "month", "is_negative_price"],
            observed=True,
        )
        .agg(
            observed_hours=("solar_mwh", "size"),
            average_solar_mwh=("solar_mwh", "mean"),
        )
        .reset_index()
    )

    solar = monthly.pivot(
        index=["year", "month"],
        columns="is_negative_price",
        values=["observed_hours", "average_solar_mwh"],
    )

    for metric in ["observed_hours", "average_solar_mwh"]:
        for category in [False, True]:
            if (metric, category) not in solar.columns:
                solar[(metric, category)] = float("nan")

    results = pd.DataFrame(index=solar.index)

    results["negative_price_hours"] = (
        solar[("observed_hours", True)].fillna(0).astype(int)
    )

    results["nonnegative_price_hours"] = (
        solar[("observed_hours", False)].fillna(0).astype(int)
    )

    results["solar_negative_price_mwh"] = solar[
        ("average_solar_mwh", True)
    ]

    results["solar_nonnegative_price_mwh"] = solar[
        ("average_solar_mwh", False)
    ]

    results["solar_difference_mwh"] = (
        results["solar_negative_price_mwh"]
        - results["solar_nonnegative_price_mwh"]
    )

    baseline = results["solar_nonnegative_price_mwh"]

    results["solar_difference_pct"] = (
        results["solar_difference_mwh"]
        .div(baseline.where(baseline.ne(0)))
        .mul(100)
    )

    results["sample_status"] = "No negative-price hours"

    has_negative = results["negative_price_hours"] > 0

    results.loc[
        has_negative
        & (results["negative_price_hours"] < MIN_NEGATIVE_HOURS),
        "sample_status",
    ] = "Small sample"

    results.loc[
        results["negative_price_hours"] >= MIN_NEGATIVE_HOURS,
        "sample_status",
    ] = "Meets 30-hour threshold"

    # A valid comparison requires observations in both price categories.
    results["comparison_available"] = (
        results["solar_negative_price_mwh"].notna()
        & results["solar_nonnegative_price_mwh"].notna()
    )

    results["solar_higher_during_negative_prices"] = (
        results["comparison_available"]
        & results["solar_difference_mwh"].gt(0)
    )

    results = results.reset_index().sort_values(["year", "month"])

    return results


def print_robustness_summary(results: pd.DataFrame) -> None:
    """Summarize consistency and sensitivity across eligible months."""

    eligible = results[
        (results["negative_price_hours"] >= MIN_NEGATIVE_HOURS)
        & results["comparison_available"]
    ].copy()

    print("\nSOLAR-GENERATION CONSISTENCY AND ROBUSTNESS")
    print(
        "Difference = negative-price average minus "
        "nonnegative-price average."
    )
    print(f"Minimum negative-price hours: {MIN_NEGATIVE_HOURS}")

    if eligible.empty:
        print("No months have enough observations for a valid comparison.")
        return

    differences = eligible["solar_difference_mwh"]
    positive_count = int(differences.gt(0).sum())
    eligible_count = len(eligible)

    print(f"\nEligible year-months: {eligible_count}")
    print(f"Positive monthly differences: {positive_count}")
    print(f"Zero or negative monthly differences: "
          f"{eligible_count - positive_count}")
    print(f"Share with higher solar generation: "
          f"{positive_count / eligible_count:.1%}")

    print("\nMONTHLY DIFFERENCE DISTRIBUTION")
    print(f"Mean difference: {differences.mean():,.1f} MWh")
    print(f"Median difference: {differences.median():,.1f} MWh")
    print(f"Smallest difference: {differences.min():,.1f} MWh")
    print(f"Largest difference: {differences.max():,.1f} MWh")

    percentage_differences = eligible["solar_difference_pct"].dropna()

    if not percentage_differences.empty:
        print(
            "Median percentage difference: "
            f"{percentage_differences.median():,.1f}%"
        )

    # Leave-one-month-out sensitivity check.
    # This checks whether the mean difference remains positive after
    # removing each eligible month in turn.
    if eligible_count >= 2:
        leave_one_out_means = [
            differences.drop(index=index).mean()
            for index in differences.index
        ]

        lowest_mean = min(leave_one_out_means)
        highest_mean = max(leave_one_out_means)

        print("\nLEAVE-ONE-MONTH-OUT SENSITIVITY")
        print(f"Lowest mean after excluding one month: {lowest_mean:,.1f} MWh")
        print(f"Highest mean after excluding one month: {highest_mean:,.1f} MWh")

        if lowest_mean > 0:
            print(
                "Interpretation: the mean monthly difference stays positive "
                "when any single eligible month is excluded."
            )
        else:
            print(
                "Interpretation: excluding at least one month can make "
                "the mean difference zero or negative."
            )

    print(
        "\nImportant: these are descriptive comparisons, not a causal test. "
        "Months are not independent experimental observations, and the "
        "30-hour cutoff is a practical screening rule, not a formal "
        "statistical significance threshold."
    )


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_FILE}. "
            "Run the data pipeline first."
        )

    data = pd.read_csv(INPUT_FILE)
    results = analyze_solar_consistency(data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_FILE, index=False)

    print("\nMONTHLY SOLAR GENERATION RESULTS")

    display_columns = [
        "year",
        "month",
        "negative_price_hours",
        "nonnegative_price_hours",
        "solar_negative_price_mwh",
        "solar_nonnegative_price_mwh",
        "solar_difference_mwh",
        "solar_difference_pct",
        "sample_status",
    ]

    print(
        results[display_columns].to_string(
            index=False,
            na_rep="N/A",
            float_format=lambda value: f"{value:,.1f}",
        )
    )

    print(f"\nResults saved to: {OUTPUT_FILE}")

    print_robustness_summary(results)


if __name__ == "__main__":
    main()
