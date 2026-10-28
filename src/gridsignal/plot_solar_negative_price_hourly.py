
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "docs"
    / "month_hour_solar_price_comparison_2024_2025.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "docs"
    / "solar_negative_price_hourly_pattern_2024_2025.png"
)

MIN_NEGATIVE_PRICE_OBSERVATIONS = 5


def load_data() -> pd.DataFrame:
    """Load and validate the month-hour comparison results."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    data = pd.read_csv(INPUT_FILE)

    required_columns = [
        "year",
        "month",
        "hour",
        "negative_price_hours",
        "solar_difference_mwh",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = data.dropna(
        subset=[
            "hour",
            "negative_price_hours",
            "solar_difference_mwh",
        ]
    ).copy()

    return data


def calculate_hourly_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate the positive-difference share by hour."""
    filtered_data = data[
        data["negative_price_hours"]
        >= MIN_NEGATIVE_PRICE_OBSERVATIONS
    ].copy()

    if filtered_data.empty:
        raise ValueError(
            "No groups meet the minimum observation threshold."
        )

    hourly_summary = (
        filtered_data
        .groupby("hour")
        .agg(
            groups=("solar_difference_mwh", "size"),
            positive_groups=(
                "solar_difference_mwh",
                lambda values: (values > 0).sum(),
            ),
            median_difference_mwh=(
                "solar_difference_mwh",
                "median",
            ),
        )
        .reset_index()
    )

    hourly_summary["positive_group_pct"] = (
        hourly_summary["positive_groups"]
        / hourly_summary["groups"]
        * 100
    )

    return hourly_summary.sort_values("hour")


def create_chart(
    hourly_summary: pd.DataFrame,
) -> None:
    """Create and save the hourly solar-generation chart."""
    if hourly_summary.empty:
        raise ValueError(
            "Hourly summary is empty. Cannot create chart."
        )

    hours = hourly_summary["hour"]
    percentages = hourly_summary["positive_group_pct"]
    group_counts = hourly_summary["groups"]

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.bar(
        hours,
        percentages,
        width=0.7,
    )

    ax.set_title(
        "Solar Generation During Negative-Price Observations",
        fontsize=15,
        pad=16,
    )

    ax.set_xlabel(
        "Hour of Day",
        fontsize=12,
    )

    ax.set_ylabel(
        "Groups with Higher Solar Generation (%)",
        fontsize=12,
    )

    ax.set_ylim(0, 110)

    ax.set_xticks(hours)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4,
    )

    ax.set_axisbelow(True)

    for bar, percentage, count in zip(
        bars,
        percentages,
        group_counts,
    ):
        ax.annotate(
            f"{percentage:.1f}%\nn={count}",
            xy=(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
            ),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.text(
        0.5,
        0.01,
        (
            "Filtered to month-hour groups with at least "
            "5 negative-price observations. "
            "Positive difference means average solar "
            "generation was higher during negative-price "
            "observations. Descriptive association only."
        ),
        ha="center",
        fontsize=9,
        wrap=True,
    )

    fig.tight_layout(
        rect=(0, 0.07, 1, 1)
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        OUTPUT_FILE,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Chart saved: {OUTPUT_FILE}")


def main() -> None:
    data = load_data()

    hourly_summary = calculate_hourly_summary(data)

    print("\nHourly summary:")
    print(
        hourly_summary[
            [
                "hour",
                "groups",
                "positive_groups",
                "positive_group_pct",
                "median_difference_mwh",
            ]
        ].round(2).to_string(index=False)
    )

    create_chart(hourly_summary)


if __name__ == "__main__":
    main()
