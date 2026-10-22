import pandas as pd

TIMEZONE = "Europe/Berlin"

GENERATION_COLUMNS = [
    "wind_offshore_mwh",
    "wind_onshore_mwh",
    "wind_total_mwh",
    "solar_mwh",
    "renewables_selected_mwh",
]


def validate_timestamps(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Validate that a dataset contains unique, valid UTC timestamps."""
    if "start_time_utc" not in df.columns:
        raise ValueError(
            f"{dataset_name} is missing the 'start_time_utc' column."
        )

    if df["start_time_utc"].isna().any():
        raise ValueError(
            f"{dataset_name} contains missing UTC timestamps."
        )

    if df["start_time_utc"].duplicated().any():
        raise ValueError(
            f"Duplicate UTC timestamps found in {dataset_name}."
        )


def combine_market_data(
    prices: pd.DataFrame,
    generation: pd.DataFrame,
) -> pd.DataFrame:
    """Validate and combine electricity prices and generation by UTC time."""
    required_price_columns = [
        "start_time_utc",
        "price_eur_mwh",
    ]
    required_generation_columns = [
        "start_time_utc",
        *GENERATION_COLUMNS,
    ]

    missing_prices = set(required_price_columns) - set(prices.columns)
    missing_generation = (
        set(required_generation_columns) - set(generation.columns)
    )

    if missing_prices:
        raise ValueError(
            f"Price data is missing columns: {sorted(missing_prices)}"
        )

    if missing_generation:
        raise ValueError(
            "Generation data is missing columns: "
            f"{sorted(missing_generation)}"
        )

    prices = prices.copy()
    generation = generation.copy()

    prices["start_time_utc"] = pd.to_datetime(
        prices["start_time_utc"],
        utc=True,
        errors="raise",
    )
    generation["start_time_utc"] = pd.to_datetime(
        generation["start_time_utc"],
        utc=True,
        errors="raise",
    )

    validate_timestamps(prices, "price data")
    validate_timestamps(generation, "generation data")

    combined = prices.merge(
        generation[
            ["start_time_utc", *GENERATION_COLUMNS]
        ],
        on="start_time_utc",
        how="outer",
        indicator=True,
        validate="one_to_one",
    )

    unmatched = combined["_merge"] != "both"

    if unmatched.any():
        unmatched_count = int(unmatched.sum())
        raise ValueError(
            f"{unmatched_count} timestamps did not match between "
            "price and generation data."
        )

    combined = combined.drop(columns="_merge")

    combined["start_time_local"] = (
        combined["start_time_utc"].dt.tz_convert(TIMEZONE)
    )
    combined["year"] = combined["start_time_local"].dt.year
    combined["month"] = combined["start_time_local"].dt.month
    combined["is_negative_price"] = (
        combined["price_eur_mwh"] < 0
    )

    return combined