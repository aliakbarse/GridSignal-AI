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
    generation = make_generation_data(
        prices["start_time_utc"].tolist()
    )

    result = combine_market_data(prices, generation)

    assert result["is_negative_price"].tolist() == [
        True,
        False,
        False,
    ]


def test_negative_price_frequency_uses_observed_hours():
    prices = make_price_data(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T01:00:00Z",
            "2024-01-01T02:00:00Z",
        ],
        [-10.0, 0.0, -5.0],
    )
    generation = make_generation_data(
        prices["start_time_utc"].tolist()
    )

    result = combine_market_data(prices, generation)

    assert result["is_negative_price"].sum() == 2
    assert len(result) == 3


def test_zero_price_is_not_a_negative_price():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z"],
        [0.0],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    result = combine_market_data(prices, generation)

    assert not result["is_negative_price"].iloc[0]


def test_market_data_combines_matching_timestamps():
    prices = make_price_data(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T01:00:00Z",
        ],
        [-5.0, 20.0],
    )
    generation = make_generation_data(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T01:00:00Z",
        ]
    )

    result = combine_market_data(prices, generation)

    assert len(result) == 2
    assert "price_eur_mwh" in result.columns
    assert "solar_mwh" in result.columns


def test_duplicate_price_timestamps_are_rejected():
    prices = make_price_data(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T00:00:00Z",
        ],
        [-5.0, -10.0],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_unmatched_timestamps_are_rejected():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z"],
        [-5.0],
    )
    generation = make_generation_data(
        ["2024-01-01T01:00:00Z"]
    )

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_missing_timestamps_are_rejected():
    prices = make_price_data(
        [None],
        [-5.0],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_missing_required_price_column_is_rejected():
    prices = pd.DataFrame(
        {
            "start_time_utc": [
                "2024-01-01T00:00:00Z"
            ]
        }
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_invalid_timestamp_strings_are_rejected():
    prices = make_price_data(
        ["not-a-timestamp"],
        [-5.0],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


# Validation tests


def test_missing_price_value_is_rejected():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z"],
        [float("nan")],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(ValueError, match="missing values"):
        combine_market_data(prices, generation)


def test_nonnumeric_price_value_is_rejected():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z"],
        ["invalid"],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(ValueError, match="nonnumeric"):
        combine_market_data(prices, generation)


def test_infinite_price_value_is_rejected():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z"],
        [float("inf")],
    )
    generation = make_generation_data(
        ["2024-01-01T00:00:00Z"]
    )

    with pytest.raises(ValueError, match="infinite"):
        combine_market_data(prices, generation)


@pytest.mark.parametrize(
    "column",
    [
        "wind_offshore_mwh",
        "wind_onshore_mwh",
        "wind_total_mwh",
        "solar_mwh",
        "renewables_selected_mwh",
    ],
)
def test_negative_generation_is_rejected(column):
    timestamps = ["2024-01-01T00:00:00Z"]

    prices = make_price_data(timestamps, [20.0])
    generation = make_generation_data(timestamps)

    generation.loc[0, column] = -1.0

    with pytest.raises(ValueError, match="negative values"):
        combine_market_data(prices, generation)


@pytest.mark.parametrize(
    "column",
    [
        "wind_offshore_mwh",
        "wind_onshore_mwh",
        "wind_total_mwh",
        "solar_mwh",
        "renewables_selected_mwh",
    ],
)
def test_missing_generation_value_is_rejected(column):
    timestamps = ["2024-01-01T00:00:00Z"]

    prices = make_price_data(timestamps, [20.0])
    generation = make_generation_data(timestamps)

    generation.loc[0, column] = float("nan")

    with pytest.raises(ValueError, match="missing values"):
        combine_market_data(prices, generation)


def test_infinite_generation_value_is_rejected():
    timestamps = ["2024-01-01T00:00:00Z"]

    prices = make_price_data(timestamps, [20.0])
    generation = make_generation_data(timestamps)

    generation.loc[0, "solar_mwh"] = float("inf")

    with pytest.raises(ValueError, match="infinite"):
        combine_market_data(prices, generation)


def test_inconsistent_total_wind_is_rejected():
    timestamps = ["2024-01-01T00:00:00Z"]

    prices = make_price_data(timestamps, [20.0])
    generation = make_generation_data(timestamps)

    generation.loc[0, "wind_total_mwh"] = 350.0

    with pytest.raises(ValueError, match="wind_total_mwh"):
        combine_market_data(prices, generation)


def test_inconsistent_selected_renewables_is_rejected():
    timestamps = ["2024-01-01T00:00:00Z"]

    prices = make_price_data(timestamps, [20.0])
    generation = make_generation_data(timestamps)

    generation.loc[0, "renewables_selected_mwh"] = 750.0

    with pytest.raises(
        ValueError,
        match="renewables_selected_mwh",
    ):
        combine_market_data(prices, generation)


def test_negative_prices_and_zero_generation_are_accepted():
    timestamps = ["2024-01-01T00:00:00Z"]

    prices = make_price_data(timestamps, [-25.0])

    generation = pd.DataFrame(
        {
            "start_time_utc": timestamps,
            "wind_offshore_mwh": [0.0],
            "wind_onshore_mwh": [0.0],
            "wind_total_mwh": [0.0],
            "solar_mwh": [0.0],
            "renewables_selected_mwh": [0.0],
        }
    )

    result = combine_market_data(prices, generation)

    assert result["price_eur_mwh"].iloc[0] == -25.0
    assert result["is_negative_price"].iloc[0]
    assert result["renewables_selected_mwh"].iloc[0] == 0.0


def test_missing_required_generation_column_is_rejected():
    timestamps = ["2024-01-01T00:00:00Z"]

    prices = make_price_data(timestamps, [20.0])
    generation = make_generation_data(timestamps)

    generation = generation.drop(columns=["solar_mwh"])

    with pytest.raises(ValueError, match="solar_mwh"):
        combine_market_data(prices, generation)


def test_duplicate_generation_timestamps_are_rejected():
    timestamps = [
        "2024-01-01T00:00:00Z",
        "2024-01-01T00:00:00Z",
    ]

    prices = make_price_data(
        ["2024-01-01T00:00:00Z"],
        [20.0],
    )
    generation = make_generation_data(timestamps)

    with pytest.raises(ValueError):
        combine_market_data(prices, generation)


def test_equivalent_timezone_timestamps_are_matched():
    prices = make_price_data(
        ["2024-01-01T00:00:00Z"],
        [20.0],
    )
    generation = make_generation_data(
        ["2024-01-01T01:00:00+01:00"]
    )

    result = combine_market_data(prices, generation)

    assert len(result) == 1
    assert result["price_eur_mwh"].iloc[0] == 20.0
    assert result["start_time_utc"].iloc[0] == pd.Timestamp(
        "2024-01-01T00:00:00Z"
    )