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


def main() -> None:
    df = pd.read_csv(DATA_FILE)

    df["start_time_utc"] = pd.to_datetime(
        df["start_time_utc"],
        utc=True,
        errors="raise",
    )

    df["start_time_local"] = (
        df["start_time_utc"]
        .dt.tz_convert("Europe/Berlin")
    )

    df["year"] = df["start_time_local"].dt.year
    df["month"] = df["start_time_local"].dt.month
    df["is_negative_price"] = df["price_eur_mwh"] < 0

    # Summarize each month and year.
    monthly = df.groupby(["year", "month"]).agg(
        hours=("price_eur_mwh", "size"),
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

    monthly["negative_price_pct"] *= 100

    # Calculate average generation separately for negative
    # and non-negative price hours within each month.
    by_category = df.groupby(
        ["year", "month", "is_negative_price"]
    ).agg(
        avg_wind_mwh=("wind_total_mwh", "mean"),
        avg_solar_mwh=("solar_mwh", "mean"),
        avg_selected_renewables_mwh=(
            "renewables_selected_mwh",
            "mean",
        ),
    )

    comparison = by_category.unstack("is_negative_price")

    comparison.columns = [
        f"{metric}_{'negative' if is_negative else 'nonnegative'}"
        for metric, is_negative in comparison.columns
    ]

    monthly = monthly.join(comparison, how="left")

    for metric in [
        "avg_wind_mwh",
        "avg_solar_mwh",
        "avg_selected_renewables_mwh",
    ]:
        negative_col = f"{metric}_negative"
        nonnegative_col = f"{metric}_nonnegative"
        difference_col = f"{metric}_difference_pct"

        if negative_col in monthly.columns and nonnegative_col in monthly.columns:
            monthly[difference_col] = (
                (monthly[negative_col] - monthly[nonnegative_col])
                / monthly[nonnegative_col].replace(0, pd.NA)
                * 100
            )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.round(2).to_csv(OUTPUT_FILE)

    print("\n--- Monthly Negative-Price Frequency ---")
    print(
        monthly[
            [
                "hours",
                "negative_price_hours",
                "negative_price_pct",
            ]
        ].round(2).to_string()
    )

    print("\n--- Monthly Generation Difference ---")
    difference_columns = [
        "avg_wind_mwh_difference_pct",
        "avg_solar_mwh_difference_pct",
        "avg_selected_renewables_mwh_difference_pct",
    ]

    print(monthly[difference_columns].round(2).to_string())

    print(f"\nResults saved to:\n{OUTPUT_FILE}")
    print(
        "\nInterpretation note: These comparisons show associations, "
        "not proof of causation."
    )


if __name__ == "__main__":
    main()
