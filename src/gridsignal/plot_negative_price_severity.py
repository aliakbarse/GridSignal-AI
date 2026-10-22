
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
    / "negative_price_severity_2024_2025.png"
)

SEVERITY_BINS = [
    float("-inf"),
    -100,
    -50,
    -20,
    -10,
    0,
]

SEVERITY_LABELS = [
    "Below -100",
    "-100 to -50",
    "-50 to -20",
    "-20 to -10",
    "-10 to 0",
]


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {DATA_FILE}\n"
            "Run the data pipeline before generating this chart."
        )

    df = pd.read_csv(DATA_FILE)

    required_columns = {"start_time_utc", "price_eur_mwh"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    df["start_time_utc"] = pd.to_datetime(
        df["start_time_utc"],
        utc=True,
        errors="raise",
    )

    df["year"] = (
        df["start_time_utc"]
        .dt.tz_convert("Europe/Berlin")
        .dt.year
    )

    df["price_eur_mwh"] = pd.to_numeric(
        df["price_eur_mwh"],
        errors="raise",
    )

    df = df[df["year"].isin([2024, 2025])].copy()
    negative = df[df["price_eur_mwh"] < 0].copy()

    if negative.empty:
        raise ValueError("No negative-price observations were found.")

    negative["severity_band"] = pd.cut(
        negative["price_eur_mwh"],
        bins=SEVERITY_BINS,
        labels=SEVERITY_LABELS,
        right=False,
    )

    counts = (
        negative.groupby(
            ["year", "severity_band"],
            observed=False,
        )
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=[2024, 2025],
            columns=SEVERITY_LABELS,
            fill_value=0,
        )
    )

    percentages = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(11, 7))

    colors = [
        "#a50f15",
        "#de2d26",
        "#fc8d59",
        "#fdd49e",
        "#74c476",
    ]

    bottom = [0.0, 0.0]

    for label, color in zip(SEVERITY_LABELS, colors):
        values = percentages[label].tolist()

        ax.bar(
            [2024, 2025],
            values,
            bottom=bottom,
            label=f"{label} EUR/MWh",
            color=color,
            width=0.58,
            edgecolor="white",
            linewidth=0.8,
        )

        for index, value in enumerate(values):
            if value >= 7:
                ax.text(
                    [2024, 2025][index],
                    bottom[index] + value / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#222222",
                )

        bottom = [
            bottom[index] + values[index]
            for index in range(2)
        ]

    ax.set_title(
        "How Severe Were Negative Electricity Prices?",
        loc="left",
        fontsize=17,
        fontweight="bold",
        pad=20,
    )

    ax.text(
        0,
        1.02,
        "Share of negative-price hours by price range, Germany",
        transform=ax.transAxes,
        fontsize=10,
        color="dimgray",
    )

    ax.set_ylabel("Share of negative-price hours (%)")
    ax.set_xlabel("")
    ax.set_xticks([2024, 2025])
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 20))
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        title="Price range",
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
    )

    fig.text(
        0.01,
        0.065,
        "KEY FINDING  |  Mild negative prices (-10 to 0 EUR/MWh) "
        "accounted for 70.0% of negative-price hours in 2024 "
        "and 76.4% in 2025.",
        fontsize=9,
        fontweight="bold",
    )

    fig.text(
        0.01,
        0.025,
        "Source: SMARD. German local time. The final three hours "
        "of 2025 are absent from the source dataset. "
        "Percentages describe observed negative-price hours only.",
        fontsize=8,
        color="dimgray",
    )

    fig.tight_layout(rect=[0, 0.12, 0.82, 0.94])

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Chart saved to:\n{OUTPUT_FILE}")
    print("\nNegative-price severity distribution (%):")
    print(percentages.round(1).to_string())


if __name__ == "__main__":
    main()
