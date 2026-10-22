
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "germany_market_combined_2024_2025.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "monthly_renewables_price_analysis.csv"
)

TIMEZONE = "Europe/Berlin"

GENERATION_METRICS = {
    "wind_total_mwh": "wind",
    "solar_mwh": "solar",
    "renewables_selected_mwh": "selected_renewables",
}


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Combined dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    required_columns = {
        "start_time_utc",
        "price_eur_mwh",
        *GENERATION_METRICS.keys(),
    }
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Combined dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    df["start_time_utc"] = pd.to_datetime(
        df["start_time_utc"],
        utc=True,
        errors="raise",
    )
    df["start_time_local"] = (
        df["start_time_utc"].dt.tz_convert(TIMEZONE)
    )

    df["year"] = df["start_time_local"].dt.year
    df["month"] = df["start_time_local"].dt.month
    df["is_negative_price"] = df["price_eur_mwh"] < 0

    monthly_keys = ["year", "month"]
    generation_columns = list(GENERATION_METRICS.keys())

    # Overall monthly price and generation statistics.
    monthly = df.groupby(monthly_keys).agg(
        observed_hours=("price_eur_mwh", "size"),
        average_price_eur_mwh=("price_eur_mwh", "mean"),
        negative_price_hours=("is_negative_price", "sum"),
        negative_price_pct=("is_negative_price", "mean"),
        avg_wind_mwh=("wind_total_mwh", "mean"),
        avg_solar_mwh=("solar_mwh", "mean"),
        avg_selected_renewables_mwh=(
            "renewables_selected_mwh",
            "mean",
        ),
    )

    monthly["negative_price_hours"] = (
        monthly["negative_price_hours"].astype(int)
    )
    monthly["nonnegative_price_hours"] = (
        monthly["observed_hours"] - monthly["negative_price_hours"]
    )
    monthly["negative_price_pct"] *= 100

    # Compare average generation across the two price categories.
    category_stats = df.groupby(
        monthly_keys + ["is_negative_price"]
    ).agg(
        hours=("price_eur_mwh", "size"),
        **{
            f"avg_{metric}_mwh": (column, "mean")
            for column, metric in GENERATION_METRICS.items()
        },
    )

    for category_value, category_name in [
        (True, "negative"),
        (False, "nonnegative"),
    ]:
        try:
            category = category_stats.xs(
                category_value,
                level="is_negative_price",
            )
        except KeyError:
            continue

        category = category.drop(columns="hours")
        category = category.rename(
            columns={
                column: f"{column}_{category_name}"
                for column in category.columns
            }
        )
        monthly = monthly.join(category, how="left")

    # Calculate absolute and relative differences.
    # Positive differences mean generation was higher during
    # negative-price hours; negative differences mean it was lower.
    for metric in GENERATION_METRICS.values():
        negative_col = f"avg_{metric}_mwh_negative"
        nonnegative_col = f"avg_{metric}_mwh_nonnegative"

        absolute_col = f"avg_{metric}_difference_mwh"
        percentage_col = f"avg_{metric}_difference_pct"

        monthly[absolute_col] = (
            monthly[negative_col] - monthly[nonnegative_col]
        )

        baseline = monthly[nonnegative_col].where(
            monthly[nonnegative_col] != 0
        )

        monthly[percentage_col] = (
            monthly[absolute_col] / baseline * 100
        )

    # A month without negative-price hours cannot support this comparison.
    no_negative_hours = monthly["negative_price_hours"] == 0

    comparison_columns = [
        column
        for column in monthly.columns
        if column.endswith("_negative")
        or "_difference_" in column
    ]
    monthly.loc[no_negative_hours, comparison_columns] = float("nan")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.round(2).to_csv(OUTPUT_FILE)

    print("\n--- Monthly Negative-Price Frequency ---")
    print(
        monthly[
            [
                "observed_hours",
                "negative_price_hours",
                "nonnegative_price_hours",
                "negative_price_pct",
                "average_price_eur_mwh",
            ]
        ].round(2).to_string()
    )

    print("\n--- Average Generation by Price Category ---")
    for metric in GENERATION_METRICS.values():
        columns = [
            f"avg_{metric}_mwh_negative",
            f"avg_{metric}_mwh_nonnegative",
            f"avg_{metric}_difference_mwh",
            f"avg_{metric}_difference_pct",
        ]

        print(f"\n{metric.replace('_', ' ').title()}")
        print(monthly[columns].round(2).to_string())

    print(f"\nResults saved to:\n{OUTPUT_FILE}")
    print(
        "\nInterpretation note: These comparisons describe associations, "
        "not proof of causation. Relative differences use average "
        "generation during nonnegative-price hours as the baseline. "
        "Comparisons are unavailable when a month has no negative-price "
        "hours."
    )


if __name__ == "__main__":
    main()
