
import pandas as pd
import pytest

from gridsignal.data_validation import combine_market_data


def make_price_data(timestamps, prices):
    return pd.DataFrame(
        {
            "start_time_utc": timestamps,
            "price_eur_mwh": prices,
        }
    )


def make_generation_data(timestamps):
    return pd.DataFrame(
        {
            "start_time_utc": timestamps,
            "wind_offshore_mwh": [100.0] * len(timestamps),
            "wind_onshore_mwh": [200.0] * len(timestamps),
            "wind_total_mwh": [300.0] * len(timestamps),
            "solar_mwh": [400.0] * len(timestamps),
            "renewables_selected_mwh": [700.0] * len(timestamps),
        }
    )


def test_negative_prices_are_identified_correctly():
    prices = make_price_data(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T01:00:00Z",
            "2024-01-01T02:00:00Z",
        ],
        [-10.0, 0.0, 25.0],
    )
    generation = make_generation_data(prices["start_time_utc"].tolist())

    result = combine_market_data(prices, generation)

    assert result["is_negative_price"].tolist() == [True, False, False]


def test_negative_price_frequency_uses_observed_hours():
    prices = make_price_data(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T01:00:00Z",
            "2024-01-01T02:00:00Z",
        ],
        [-10.0, 0.0, -5.0],
    )
    generation = make_generation_data(prices["start_time_utc"].tolist())

    result = combine_market_data(prices, generation)

    assert result["is_negative_price"].sum() == 2
    assert len(result) == 3


def test_zero_price_is_not_a_negative_price():
    prices = make_price_data(["2024-01-01T00:00:00Z"], [0.0])
    generation = make_generation_data(["2024-01-01T00:00:00Z"])

    result = combine_market_data(prices, generation)

    assert not result["is_negative_price"].iloc[0]


def test_market_data_combines_matching_timestamps():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
        [-5.0, 20.0],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"]
    )

    result = combine_market_data(prices, generation)

    assert len(result) == 2
    assert "price_eur_mwh" in result.columns
    assert "solar_mwh" in result.columns


def test_duplicate_price_timestamps_are_rejected():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"],
        [-5.0, -10.0],
    )
    generation = make_generation_data(["2024-01-01T00:00:00Z"])

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_unmatched_timestamps_are_rejected():
    prices = make_price_data(["2024-01-01T00:00:00Z"], [-5.0])
    generation = make_generation_data(["2024-01-01T01:00:00Z"])

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_missing_timestamps_are_rejected():
    prices = make_price_data([None], [-5.0])
    generation = make_generation_data(["2024-01-01T00:00:00Z"])

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_missing_required_price_column_is_rejected():
    prices = pd.DataFrame(
        {"start_time_utc": ["2024-01-01T00:00:00Z"]}
    )
    generation = make_generation_data(["2024-01-01T00:00:00Z"])

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_invalid_timestamp_strings_are_rejected():
    """Invalid timestamp strings must not silently enter the join."""
    prices = make_price_data(["not-a-timestamp"], [-5.0])
    generation = make_generation_data(["2024-01-01T00:00:00Z"])

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)
