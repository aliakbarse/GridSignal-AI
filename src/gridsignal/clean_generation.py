from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Actual_generation_202312312100_202512312100_Hour.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "germany_generation_2024_2025.csv"
)

TIMEZONE = "Europe/Berlin"


def main() -> None:
    df = pd.read_csv(
        RAW_FILE,
        sep=";",
        thousands=",",
        na_values=["-"],
    )

    df["Start date"] = pd.to_datetime(
        df["Start date"],
        format="%b %d, %Y %I:%M %p",
        errors="raise",
    )

    df["End date"] = pd.to_datetime(
        df["End date"],
        format="%b %d, %Y %I:%M %p",
        errors="raise",
    )

    clean = df[
        [
            "Start date",
            "End date",
            "Wind offshore [MWh] Calculated resolutions",
            "Wind onshore [MWh] Calculated resolutions",
            "Photovoltaics [MWh] Calculated resolutions",
        ]
    ].copy()

    clean = clean.rename(
        columns={
            "Start date": "start_time_local",
            "End date": "end_time_local",
            "Wind offshore [MWh] Calculated resolutions":
                "wind_offshore_mwh",
            "Wind onshore [MWh] Calculated resolutions":
                "wind_onshore_mwh",
            "Photovoltaics [MWh] Calculated resolutions":
                "solar_mwh",
        }
    )

    generation_columns = [
        "wind_offshore_mwh",
        "wind_onshore_mwh",
        "solar_mwh",
    ]

    clean[generation_columns] = clean[generation_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    clean = clean.dropna(
        subset=["start_time_local", "end_time_local"]
        + generation_columns
    )

    clean = clean.sort_values(
        "start_time_local",
        kind="stable",
    ).reset_index(drop=True)

    clean["start_time_berlin"] = (
        clean["start_time_local"].dt.tz_localize(
            TIMEZONE,
            ambiguous="infer",
            nonexistent="raise",
        )
    )

    clean["start_time_utc"] = (
        clean["start_time_berlin"].dt.tz_convert("UTC")
    )

    clean["wind_total_mwh"] = (
        clean["wind_offshore_mwh"]
        + clean["wind_onshore_mwh"]
    )

    clean["renewables_selected_mwh"] = (
        clean["wind_total_mwh"] + clean["solar_mwh"]
    )

    print("\n--- Generation Data Quality Report ---")
    print(f"Rows: {len(clean):,}")
    print(f"Duplicate UTC timestamps: "
          f"{clean['start_time_utc'].duplicated().sum()}")
    print(f"Missing generation values: "
          f"{clean[generation_columns].isna().sum().sum()}")
    print(f"First timestamp: {clean['start_time_local'].min()}")
    print(f"Last timestamp: {clean['start_time_local'].max()}")

    utc_diffs = clean["start_time_utc"].diff().dropna()
    irregular = (utc_diffs != pd.Timedelta(hours=1)).sum()
    print(f"Non-hourly UTC gaps: {irregular}")

    output_columns = [
        "start_time_local",
        "end_time_local",
        "start_time_utc",
        "wind_offshore_mwh",
        "wind_onshore_mwh",
        "wind_total_mwh",
        "solar_mwh",
        "renewables_selected_mwh",
    ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean[output_columns].to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved cleaned data to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
