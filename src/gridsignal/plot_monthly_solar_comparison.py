
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path("data/processed/germany_market_combined_2024_2025.csv")
OUTPUT_FILE = Path("docs/monthly_solar_comparison_2024_2025.png")

MIN_NEGATIVE_HOURS = 30

REQUIRED_COLUMNS = [
    "start_time_utc",
    "price_eur_mwh",
    "solar_mwh",
]


def prepare_monthly_data(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly average solar generation by price category."""

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
    df["price_eur_mwh"] = pd.to_numeric(
        df["price_eur_mwh"],
        errors="coerce",
    )
    df["solar_mwh"] = pd.to_numeric(
        df["solar_mwh"],
        errors="coerce",
    )

    if df.isna().any().any():
        raise ValueError(
            "Input contains missing or invalid timestamps or numeric values."
        )

    local_time = df["start_time_utc"].dt.tz_convert("Europe/Berlin")
    df["year"] = local_time.dt.year
    df["month"] = local_time.dt.month

    df = df[df["year"].isin([2024, 2025])].copy()

    df["price_category"] = (
        df["price_eur_mwh"]
        .lt(0)
        .map({
            True: "Negative price",
            False: "Nonnegative price",
        })
    )

    monthly = (
        df.groupby(
            ["year", "month", "price_category"],
            observed=True,
        )
        .agg(
            observed_hours=("solar_mwh", "size"),
            average_solar_mwh=("solar_mwh", "mean"),
        )
        .reset_index()
    )

    expected = pd.MultiIndex.from_product(
        [
            [2024, 2025],
            range(1, 13),
            ["Negative price", "Nonnegative price"],
        ],
        names=["year", "month", "price_category"],
    )

    monthly = (
        monthly.set_index(["year", "month", "price_category"])
        .reindex(expected)
        .reset_index()
    )

    monthly["observed_hours"] = (
        monthly["observed_hours"].fillna(0).astype(int)
    )

    # Explicitly preserve missing averages when a category has no observations.
    # In particular, zero negative-price hours must never mean zero generation.
    monthly.loc[
        monthly["observed_hours"] == 0,
        "average_solar_mwh",
    ] = float("nan")

    negative_counts = (
        df.assign(is_negative=df["price_eur_mwh"].lt(0))
        .groupby(["year", "month"], as_index=False)
        .agg(negative_price_hours=("is_negative", "sum"))
    )

    monthly = monthly.merge(
        negative_counts,
        on=["year", "month"],
        how="left",
        validate="many_to_one",
    )

    monthly["negative_price_hours"] = (
        monthly["negative_price_hours"].fillna(0).astype(int)
    )

    return monthly



def create_chart(monthly: pd.DataFrame) -> None:
    """Plot monthly solar averages with aligned sample-count strips."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(12, 10))

    grid = fig.add_gridspec(
        nrows=4,
        ncols=1,
        height_ratios=[4, 0.8, 4, 0.8],
        hspace=0.12,
    )

    ax_2024 = fig.add_subplot(grid[0])
    count_ax_2024 = fig.add_subplot(grid[1], sharex=ax_2024)
    ax_2025 = fig.add_subplot(grid[2], sharex=ax_2024)
    count_ax_2025 = fig.add_subplot(grid[3], sharex=ax_2024)

    chart_axes = {2024: ax_2024, 2025: ax_2025}
    count_axes = {2024: count_ax_2024, 2025: count_ax_2025}

    months = list(range(1, 13))
    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    categories = [
        ("Nonnegative price", "Nonnegative-price hours", "o"),
        ("Negative price", "Negative-price hours", "s"),
    ]

    for year in [2024, 2025]:
        year_data = monthly[monthly["year"] == year]
        ax = chart_axes[year]
        count_ax = count_axes[year]

        for category, label, marker in categories:
            category_data = (
                year_data[year_data["price_category"] == category]
                .set_index("month")
                .reindex(months)
            )

            values = category_data["average_solar_mwh"].copy()
            no_observations = (
                category_data["observed_hours"].fillna(0) == 0
            )
            values.loc[no_observations] = float("nan")

            ax.plot(
                months,
                values,
                marker=marker,
                linewidth=2,
                markersize=5,
                label=label,
            )

        ax.set_title(f"{year}", loc="left", fontweight="bold")
        ax.set_ylabel("Average solar generation (MWh)")
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.legend(frameon=False, loc="upper left")
        ax.set_xlim(0.5, 12.5)

        count_ax.set_ylim(0, 1)
        count_ax.set_yticks([])
        count_ax.set_ylabel(
            "Sample\ncount",
            rotation=0,
            labelpad=36,
            va="center",
        )
        count_ax.set_xticks(months)
        count_ax.set_xticklabels(month_labels)
        count_ax.tick_params(axis="x", length=0, labelsize=9)

        for spine in count_ax.spines.values():
            spine.set_visible(False)

        for month in months:
            row = year_data[
                (year_data["month"] == month)
                & (year_data["price_category"] == "Negative price")
            ]
            count = int(row["negative_price_hours"].iloc[0])

            if count == 0:
                label = "n=0"
            elif count < MIN_NEGATIVE_HOURS:
                label = f"n={count}*"
            else:
                label = f"n={count}"

            count_ax.text(
                month,
                0.55,
                label,
                ha="center",
                va="center",
                fontsize=8,
            )

    # Suppress month labels on both main charts.
    # The labels will appear only in the sample-count strips.
    ax_2024.tick_params(axis="x", labelbottom=False)
    ax_2025.tick_params(axis="x", labelbottom=False)

    fig.suptitle(
        "Solar Generation During Negative-Price Hours",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    fig.text(
        0.5,
        0.945,
        "Germany | Monthly averages, 2024–2025 | "
        "Negative prices are below €0/MWh",
        ha="center",
        fontsize=9,
    )

    fig.text(
        0.5,
        0.025,
        "* Fewer than 30 negative-price hours; interpret cautiously. "
        "n=0 means no negative-price observations were available.",
        ha="center",
        fontsize=8,
    )

    fig.subplots_adjust(
        left=0.12,
        right=0.97,
        top=0.91,
        bottom=0.08,
    )

    fig.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Chart saved to: {OUTPUT_FILE}")



def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}\n"
            "Run the data-cleaning and combining pipeline first."
        )

    data = pd.read_csv(INPUT_FILE)
    monthly = prepare_monthly_data(data)
    create_chart(monthly)


if __name__ == "__main__":
    main()
