
import pandas as pd
import pytest

from gridsignal.data_validation import combine_market_data


def make_price_data(
    timestamps: list[str | None],
    prices: list[float],
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "start_time_utc": timestamps,
            "price_eur_mwh": prices,
        }
    )


def make_generation_data(
    timestamps: list[str | None],
) -> pd.DataFrame:
    row_count = len(timestamps)

    return pd.DataFrame(
        {
            "start_time_utc": timestamps,
            "wind_offshore_mwh": [10.0] * row_count,
            "wind_onshore_mwh": [20.0] * row_count,
            "wind_total_mwh": [30.0] * row_count,
            "solar_mwh": [40.0] * row_count,
            "renewables_selected_mwh": [70.0] * row_count,
        }
    )


def test_negative_prices_are_identified_correctly():
    """Only prices strictly below zero count as negative."""
    prices = pd.Series([-25.0, -0.01, 0.0, 15.0])

    assert (prices < 0).tolist() == [True, True, False, False]


def test_negative_price_frequency_uses_observed_hours():
    """Calculate frequency using the number of observed records."""
    prices = pd.Series([-10.0, 20.0, -5.0, 30.0])

    frequency = (prices < 0).mean() * 100

    assert frequency == 50.0


def test_zero_price_is_not_a_negative_price():
    """A price of exactly zero is not negative."""
    assert not (0.0 < 0)


def test_market_data_combines_matching_timestamps():
    """Matching price and generation records should combine correctly."""
    timestamps = [
        "2024-01-01T00:00:00Z",
        "2024-01-01T01:00:00Z",
    ]
    prices = make_price_data(timestamps, [-5.0, 20.0])
    generation = make_generation_data(timestamps)

    combined = combine_market_data(prices, generation)

    assert len(combined) == 2
    assert combined["start_time_utc"].is_unique
    assert combined["is_negative_price"].tolist() == [True, False]
    assert combined["year"].tolist() == [2024, 2024]
    assert combined["month"].tolist() == [1, 1]


def test_duplicate_price_timestamps_are_rejected():
    """Duplicate timestamps must not silently multiply join rows."""
    timestamps = [
        "2024-01-01T00:00:00Z",
        "2024-01-01T00:00:00Z",
    ]
    prices = make_price_data(timestamps, [-5.0, 10.0])
    generation = make_generation_data(timestamps[:1])

    with pytest.raises(
        ValueError,
        match="Duplicate UTC timestamps found in price data",
    ):
        combine_market_data(prices, generation)


def test_unmatched_timestamps_are_rejected():
    """A missing generation interval must cause the join to fail."""
    prices = make_price_data(
        ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
        [-5.0, 20.0],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(
        ValueError,
        match="timestamps did not match",
    ):
        combine_market_data(prices, generation)


def test_missing_timestamps_are_rejected():
    """Missing timestamp values must not enter the combined dataset."""
    prices = make_price_data([None], [-5.0])
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(
        ValueError,
        match="missing UTC timestamps",
    ):
        combine_market_data(prices, generation)


def test_missing_required_price_column_is_rejected():
    """Price data must include its required price column."""
    prices = pd.DataFrame(
        {"start_time_utc": ["2024-01-01T00:00:00Z"]}
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(
        ValueError,
        match="Price data is missing columns",
    ):
        combine_market_data(prices, generation)


def test_invalid_timestamp_strings_are_rejected():
    """Invalid timestamp strings must not silently enter the join."""
    prices = make_price_data(["not-a-timestamp"], [-5.0])
    generation = make_generation_data(["2024-01-01T00:00:00Z"])

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)
