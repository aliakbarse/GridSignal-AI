
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


OUTPUT_DIR = Path("docs")

FREQUENCY_FILE = (
    OUTPUT_DIR / "hourly_negative_price_frequency_2024_2025.csv"
)
SOLAR_FILE = (
    OUTPUT_DIR / "hourly_solar_by_price_category_2024_2025.csv"
)
OUTPUT_FILE = OUTPUT_DIR / "hour_of_day_analysis_2024_2025.png"

HOURS = list(range(24))

# Use a consistent visual identity across all panels.
COLORS = {
    "2024": "#4776A8",
    "2025": "#D97736",
    "Negative price": "#C65353",
    "Nonnegative price": "#4776A8",
}


def load_data():
    """Load and validate the hourly analysis outputs."""
    for path in [FREQUENCY_FILE, SOLAR_FILE]:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}\n"
                "Run analyze_hour_of_day.py first."
            )

    frequency = pd.read_csv(FREQUENCY_FILE)
    solar = pd.read_csv(SOLAR_FILE)

    required_frequency = {
        "year",
        "hour",
        "observed_hours",
        "negative_price_hours",
        "negative_price_rate_pct",
    }
    required_solar = {
        "year",
        "hour",
        "price_category",
        "observed_hours",
        "average_solar_mwh",
    }

    if not required_frequency.issubset(frequency.columns):
        missing = required_frequency - set(frequency.columns)
        raise ValueError(
            f"Frequency file is missing columns: {sorted(missing)}"
        )

    if not required_solar.issubset(solar.columns):
        missing = required_solar - set(solar.columns)
        raise ValueError(
            f"Solar file is missing columns: {sorted(missing)}"
        )

    return frequency, solar


def style_axis(ax):
    """Apply consistent styling to a chart axis."""
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels(
        [f"{hour:02d}:00" for hour in range(0, 24, 2)]
    )
    ax.grid(axis="y", alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_frequency(ax, frequency):
    """Plot negative-price rates by local hour."""
    for year in sorted(frequency["year"].unique()):
        year_data = (
            frequency[frequency["year"] == year]
            .sort_values("hour")
        )

        ax.plot(
            year_data["hour"],
            year_data["negative_price_rate_pct"],
            color=COLORS[str(year)],
            linewidth=2.4,
            marker="o",
            markersize=4,
            label=str(year),
        )

    # Mark the highest observed rate in each year.
    for year in sorted(frequency["year"].unique()):
        year_data = frequency[frequency["year"] == year]
        peak = year_data.loc[
            year_data["negative_price_rate_pct"].idxmax()
        ]

        ax.annotate(
            f"{int(year)} peak\n"
            f"{int(peak['hour']):02d}:00 · "
            f"{peak['negative_price_rate_pct']:.1f}%",
            xy=(
                peak["hour"],
                peak["negative_price_rate_pct"],
            ),
            xytext=(0, 12 if int(year) == 2024 else -32),
            textcoords="offset points",
            color=COLORS[str(year)],
            fontsize=8.5,
            ha="center",
            arrowprops={
                "arrowstyle": "-",
                "color": COLORS[str(year)],
                "alpha": 0.7,
                "linewidth": 0.8,
            },
        )

    ax.set_title(
        "A. Negative-price frequency by hour",
        loc="left",
        fontweight="bold",
        pad=12,
    )
    ax.set_ylabel("Observed hours with negative prices (%)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    style_axis(ax)


def plot_solar_year(ax, solar, year):
    """Compare solar generation by price category for one year."""
    year_data = solar[solar["year"] == year]

    for category in ["Nonnegative price", "Negative price"]:
        category_data = (
            year_data[year_data["price_category"] == category]
            .sort_values("hour")
        )

        # A line is shown only for hours with observed data in
        # this category. Missing combinations remain gaps.
        ax.plot(
            category_data["hour"],
            category_data["average_solar_mwh"],
            color=COLORS[category],
            linewidth=2.3,
            marker="o",
            markersize=3.5,
            label=category,
        )

    # The overnight negative-price averages often have very small
    # samples. Flag those points rather than hiding their uncertainty.
    negative_data = year_data[
        year_data["price_category"] == "Negative price"
    ]

    sparse = negative_data[
        negative_data["observed_hours"] < 30
    ]

    if not sparse.empty:
        ax.scatter(
            sparse["hour"],
            sparse["average_solar_mwh"],
            s=48,
            facecolors="none",
            edgecolors=COLORS["Negative price"],
            linewidths=1.3,
            zorder=5,
            label="Negative-price hours: n < 30",
        )

    ax.set_title(
        f"{'B' if year == 2024 else 'C'}. Average solar generation — {year}",
        loc="left",
        fontweight="bold",
        pad=12,
    )
    ax.set_ylabel("Average solar generation (MWh)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    style_axis(ax)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    frequency, solar = load_data()

    fig = plt.figure(figsize=(15, 11), layout="constrained")
    grid = fig.add_gridspec(
        nrows=2,
        ncols=2,
        height_ratios=[1, 1.15],
    )

    ax_frequency = fig.add_subplot(grid[0, :])
    ax_solar_2024 = fig.add_subplot(grid[1, 0])
    ax_solar_2025 = fig.add_subplot(grid[1, 1])

    plot_frequency(ax_frequency, frequency)
    plot_solar_year(ax_solar_2024, solar, 2024)
    plot_solar_year(ax_solar_2025, solar, 2025)

    fig.suptitle(
        "Germany's Day-Ahead Electricity Market | 2024–2025",
        fontsize=17,
        fontweight="bold",
    )

    fig.text(
        0.5,
        -0.015,
        "German local time. Negative prices are below €0/MWh. "
        "Solar averages are descriptive, not causal; "
        "outlined points have fewer than 30 negative-price observations.",
        ha="center",
        fontsize=9,
        wrap=True,
    )

    fig.savefig(
        OUTPUT_FILE,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)

    print(f"Visualization saved: {OUTPUT_FILE}")
    print("Chart contains:")
    print("  A. Negative-price frequency by hour for 2024 and 2025")
    print("  B. Average solar generation by price category in 2024")
    print("  C. Average solar generation by price category in 2025")


if __name__ == "__main__":
    main()
