
from pathlib import Path

import matplotlib.pyplot as plt
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
    / "docs"
    / "negative_price_frequency_2024_2025.png"
)


def main() -> None:
    df = pd.read_csv(DATA_FILE)

    df["start_time_utc"] = pd.to_datetime(
        df["start_time_utc"],
        utc=True,
        errors="raise",
    )
    df["start_time_local"] = (
        df["start_time_utc"].dt.tz_convert("Europe/Berlin")
    )

    df["year"] = df["start_time_local"].dt.year
    df["month"] = df["start_time_local"].dt.month
    df["is_negative_price"] = df["price_eur_mwh"] < 0

    monthly = (
        df.groupby(["year", "month"])
        .agg(
            observed_hours=("price_eur_mwh", "size"),
            negative_hours=("is_negative_price", "sum"),
        )
        .reset_index()
    )

    monthly["negative_price_pct"] = (
        monthly["negative_hours"]
        / monthly["observed_hours"]
        * 100
    )

    plot_data = monthly.pivot(
        index="month",
        columns="year",
        values="negative_price_pct",
    )

    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    fig, ax = plt.subplots(figsize=(11, 6.5))

    for year in [2024, 2025]:
        if year in plot_data.columns:
            ax.plot(
                plot_data.index,
                plot_data[year],
                marker="o",
                linewidth=2.5,
                markersize=6,
                label=str(year),
            )

    # Highlight the highest monthly value in 2025.
    june_2025 = plot_data.loc[6, 2025]

    ax.annotate(
        f"June 2025 peak: {june_2025:.1f}%",
        xy=(6, june_2025),
        xytext=(7.0, june_2025 + 0.5),
        fontsize=9,
        fontweight="bold",
        arrowprops={
            "arrowstyle": "->",
            "connectionstyle": "arc3,rad=0.15",
            "linewidth": 1.2,
        },
    )

    ax.set_title(
        "Negative Electricity Prices in Germany",
        loc="left",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )

    ax.text(
        0,
        1.02,
        "Monthly share of observed hours with prices below €0/MWh",
        transform=ax.transAxes,
        fontsize=10,
        color="dimgray",
    )

    ax.set_xlabel("")
    ax.set_ylabel("Hours with negative prices (%)")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_labels)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(title="Year", frameon=False)

    fig.text(
        0.01,
        0.055,
        "KEY TAKEAWAY  |  Negative-price frequency surged in May 2025, "
        "peaked at 19.6% in June, then fell to 1.6% in July.",
        fontsize=9,
        fontweight="bold",
    )

    fig.text(
        0.01,
        0.015,
        "Source: SMARD. German local time. 2025 excludes the final "
        "three hours of the year; percentages use observed hours.",
        fontsize=8,
        color="dimgray",
    )

    fig.tight_layout(rect=[0, 0.10, 1, 0.95])

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Chart saved to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()