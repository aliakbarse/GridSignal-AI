import numpy as np
import pandas as pd

TIMEZONE = "Europe/Berlin"

GENERATION_COLUMNS = [
    "wind_offshore_mwh",
    "wind_onshore_mwh",
    "wind_total_mwh",
    "solar_mwh",
    "renewables_selected_mwh",
]

NUMERIC_COLUMNS = [
    "price_eur_mwh",
    *GENERATION_COLUMNS,
]

GENERATION_COMPONENT_COLUMNS = [
    "wind_offshore_mwh",
    "wind_onshore_mwh",
    "wind_total_mwh",
    "solar_mwh",
    "renewables_selected_mwh",
]

DERIVED_COLUMNS = {
    "wind_total_mwh": [
        "wind_onshore_mwh",
        "wind_offshore_mwh",
    ],
    "renewables_selected_mwh": [
        "solar_mwh",
        "wind_total_mwh",
    ],
}

NUMERIC_TOLERANCE = 1e-9


def validate_timestamps(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Validate that a dataset contains unique, valid UTC timestamps."""
    if "start_time_utc" not in df.columns:
        raise ValueError(
            f"{dataset_name} is missing the 'start_time_utc' column."
        )

    timestamps = df["start_time_utc"]

    if timestamps.isna().any():
        raise ValueError(
            f"{dataset_name} contains missing UTC timestamps."
        )

    if not isinstance(timestamps.dtype, pd.DatetimeTZDtype):
        raise ValueError(
            f"{dataset_name} timestamps must be timezone-aware UTC datetimes."
        )

    if str(timestamps.dt.tz) != "UTC":
        raise ValueError(
            f"{dataset_name} timestamps must use the UTC timezone."
        )

    if timestamps.duplicated().any():
        raise ValueError(
            f"Duplicate UTC timestamps found in {dataset_name}."
        )


def validate_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
    dataset_name: str,
) -> None:
    """Validate numeric columns and reject missing or infinite values."""
    for column in columns:
        if column not in df.columns:
            raise ValueError(
                f"{dataset_name} is missing the '{column}' column."
            )

        try:
            numeric_values = pd.to_numeric(
                df[column],
                errors="raise",
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{dataset_name} contains nonnumeric values "
                f"in '{column}'."
            ) from error

        if numeric_values.isna().any():
            raise ValueError(
                f"{dataset_name} contains missing values "
                f"in '{column}'."
            )

        if not np.isfinite(numeric_values).all():
            raise ValueError(
                f"{dataset_name} contains infinite values "
                f"in '{column}'."
            )

        df[column] = numeric_values


def validate_generation_values(
    generation: pd.DataFrame,
) -> None:
    """Validate generation values and derived generation totals."""
    validate_numeric_columns(
        generation,
        GENERATION_COLUMNS,
        "generation data",
    )

    for column in GENERATION_COMPONENT_COLUMNS:
        if (generation[column] < 0).any():
            raise ValueError(
                "Generation data contains negative values "
                f"in '{column}'."
            )

    for derived_column, component_columns in DERIVED_COLUMNS.items():
        expected_total = generation[component_columns].sum(axis=1)

        matches = np.isclose(
            generation[derived_column],
            expected_total,
            rtol=NUMERIC_TOLERANCE,
            atol=NUMERIC_TOLERANCE,
        )

        if not matches.all():
            mismatch_count = int((~matches).sum())

            raise ValueError(
                f"Generation data contains {mismatch_count} "
                f"inconsistent values in '{derived_column}'. "
                f"Expected the sum of {component_columns}."
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

    missing_prices = (
        set(required_price_columns) - set(prices.columns)
    )

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

    validate_numeric_columns(
        prices,
        ["price_eur_mwh"],
        "price data",
    )

    validate_generation_values(generation)

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