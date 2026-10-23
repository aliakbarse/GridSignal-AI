# GridSignal AI

**An evidence-grounded intelligence assistant for the German electricity market.**

GridSignal AI is a portfolio project exploring how electricity-market analytics, forecasting, and retrieval-augmented generation (RAG) can work together to explain market conditions using quantitative data and traceable evidence.

The current implementation is a reproducible Python analytics pipeline examining German day-ahead electricity prices and selected renewable-generation data for 2024–2025. Future development will introduce forecasting, evidence retrieval, and AI-assisted explanations.

## Research Question

How did negative electricity prices vary across months and hours in 2024 and 2025, and how did wind and solar generation differ between negative-price and nonnegative-price hours?

## Key Findings

### 1. Negative prices became more frequent in May and June 2025

| Month | Negative-price hours in 2024 | Frequency in 2024 | Negative-price hours in 2025 | Frequency in 2025 |
|---|---:|---:|---:|---:|
| May | 78 | 10.48% | 129 | 17.34% |
| June | 64 | 8.89% | 141 | 19.58% |

June 2025 recorded the highest observed monthly negative-price frequency in the dataset: **19.58% of observed hours**, compared with 8.89% in June 2024.

Negative-price frequency subsequently fell to 1.61% in July 2025. These changes identify periods worth investigating, but do not independently explain the underlying market conditions.

### 2. Solar generation was higher during negative-price hours

In May 2025, average solar generation was approximately 34,775 MWh during negative-price hours, compared with 9,415 MWh during nonnegative-price hours.

In June 2025, the corresponding averages were approximately 35,296 MWh and 9,713 MWh.

These figures represent average generation per observed hourly interval, not monthly generation totals. The association does not establish causation: demand, conventional generation, cross-border electricity flows, storage, and other market conditions may also influence prices.

### 3. Most negative-price hours occurred in the mildest negative-price range

The dataset contained 457 negative-price hours in 2024 and 573 in 2025, an increase of approximately 25.4%.

| Negative-price range | 2024 hours | Share of 2024 negative hours | 2025 hours | Share of 2025 negative hours |
|---|---:|---:|---:|---:|
| Below −100 €/MWh | 5 | 1.1% | 13 | 2.3% |
| −100 to −50 €/MWh | 22 | 4.8% | 17 | 3.0% |
| −50 to −20 €/MWh | 61 | 13.3% | 54 | 9.4% |
| −20 to −10 €/MWh | 49 | 10.7% | 51 | 8.9% |
| −10 to 0 €/MWh | 320 | 70.0% | 438 | 76.4% |

Although negative-price hours increased, most remained between −10 and 0 €/MWh. The annual minimum reached −250.32 €/MWh in 2025, compared with −135.45 €/MWh in 2024.

This distinction shows why the frequency of negative prices and their severity should be analyzed separately.

### 4. Higher solar generation during negative-price hours was consistent across selected months

Across the 13 year-month combinations with at least 30 negative-price hours, average solar generation was higher during negative-price hours in all 13 cases.

The mean difference was approximately 20,334 MWh per observed hourly interval, and the median difference was approximately 19,168 MWh.

This consistency strengthens the descriptive finding within the selected observations. However, the threshold is a practical inclusion rule, not a statistical significance test. The result does not prove that solar generation caused negative prices.

### 5. Negative-price frequency peaked around midday

The hour of day with the highest negative-price frequency differed slightly between years:

- **2024:** 14:00 local time, with 75 negative-price hours out of 366 observed hours (20.49%).
- **2025:** 13:00 local time, with 99 negative-price hours out of 365 observed hours (27.12%).

The peak frequency was approximately 6.63 percentage points higher in 2025. The midday concentration identifies a useful pattern for further investigation, but does not establish why prices became negative.

### 6. The hourly comparison also showed higher solar generation during negative-price hours

The hourly analysis compared average solar generation during negative-price and nonnegative-price hours for each local hour of the day.

For example, at 11:00 in 2025, average solar generation was approximately 35,216 MWh during negative-price hours, compared with 22,946 MWh during nonnegative-price hours — a difference of approximately 12,270 MWh, or 53%.

Some overnight comparisons contain relatively few negative-price observations. Those results should be interpreted cautiously, particularly where fewer than 30 negative-price observations are available.

## Visualizations

### Monthly negative-price frequency

![Monthly frequency of negative electricity prices in Germany, 2024–2025](docs/negative_price_frequency_2024_2025.png)

Monthly share of observed hourly intervals with day-ahead prices below 0 €/MWh.

### Negative-price severity

![Severity distribution of negative electricity prices in Germany, 2024–2025](docs/negative_price_severity_2024_2025.png)

Annual distribution of negative-price hours across five price-severity ranges.

### Monthly solar comparison

![Monthly average solar generation during negative-price and nonnegative-price hours](docs/monthly_solar_comparison_2024_2025.png)

Compares average solar generation across months and price categories. Values represent average generation per observed interval, not monthly totals.

### Hour-of-day analysis

![Hourly negative-price frequency and solar generation by price category, 2024–2025](docs/hour_of_day_analysis_2024_2025.png)

Shows negative-price frequency by local hour and compares average solar generation between negative-price and nonnegative-price hours.

The written analysis and additional supporting tables are available in [`docs/findings.md`](docs/findings.md).

## Data Sources

**Primary source:** [SMARD — Germany's electricity market data platform](https://www.smard.de/en)

The project uses hourly data for the Germany/Luxembourg bidding zone:

- Day-ahead electricity prices (€/MWh)
- Actual offshore wind generation
- Actual onshore wind generation
- Actual solar generation

The selected generation measures do not represent total electricity supply or every renewable energy source.

### Data quality and limitations

- The 2024 dataset contains 8,784 hourly records, covering the leap year.
- The 2025 dataset contains 8,757 hourly records. The final three hours of the year are absent from the downloaded source data.
- The combined dataset contains 17,541 matched hourly price and generation records.
- Price and generation records are joined using UTC timestamps.
- German local time (`Europe/Berlin`) is used for calendar-year, monthly, seasonal, and hour-of-day analysis.
- Daylight-saving transitions mean that local months and individual local hours can contain different numbers of observations.
- Negative-price frequency is calculated using observed hourly records as the denominator.
- Months with no negative-price hours cannot support comparisons between negative-price and nonnegative-price hours.
- Some hour-of-day comparisons have relatively few negative-price observations.
- The analysis is descriptive and does not establish causal relationships or demonstrate statistical significance.
- Generation values follow the downloaded source data. Source definitions, units, and any estimates should be verified before publication or commercial interpretation.

These limitations matter when comparing periods, interpreting averages, and drawing conclusions about market behavior.

## Methodology

The current workflow follows these stages:

1. **Inspect:** Examine source files, columns, timestamp formats, and data quality.
2. **Clean:** Parse timestamps and numerical values, handle missing data, and normalize timestamps.
3. **Validate:** Check required columns, timestamp uniqueness, missing intervals, and matching price and generation records.
4. **Combine:** Join prices and selected generation measures using UTC timestamps.
5. **Analyze:** Calculate negative-price frequency, compare generation across price categories, examine severity, and summarize patterns by month, season, and hour of day.
6. **Visualize:** Generate charts that communicate the principal patterns and support further investigation.
7. **Document:** Record findings, assumptions, limitations, and supporting outputs.

The workflow is generated locally from downloaded source files using Python and pandas.

## Repository Structure

```text
GridSignal_AI/
├── data/
│   ├── raw/                       # Original source files (local)
│   └── processed/                 # Generated datasets (local)
├── docs/
│   ├── findings.md
│   ├── negative_price_frequency_2024_2025.png
│   ├── negative_price_severity_2024_2025.png
│   ├── monthly_solar_comparison_2024_2025.png
│   ├── hour_of_day_analysis_2024_2025.png
│   ├── monthly_solar_consistency_2024_2025.csv
│   ├── hourly_negative_price_frequency_2024_2025.csv
│   ├── hourly_solar_by_price_category_2024_2025.csv
│   └── seasonal_price_and_solar_summary_2024_2025.csv
├── src/
│   └── gridsignal/
│       ├── inspect_data.py
│       ├── clean_data.py
│       ├── clean_generation.py
│       ├── data_validation.py
│       ├── combine_data.py
│       ├── analyze_prices.py
│       ├── analyze_generation_by_price.py
│       ├── analyze_monthly_generation.py
│       ├── analyze_solar_consistency.py
│       ├── analyze_hour_of_day.py
│       ├── plot_negative_price_frequency.py
│       ├── plot_negative_price_severity.py
│       ├── plot_monthly_solar_comparison.py
│       └── plot_hour_of_day_analysis.py
├── tests/
│   └── test_data_pipeline.py
├── .gitignore
├── pyproject.toml
└── README.md
```

Raw and processed datasets are excluded from version control. The charts, analysis scripts, supporting summaries, and written findings are intended to be included in the repository.

## Run the Project Locally

### Requirements

- Python 3.14 or later, as specified in the current project configuration
- pip
- Git

### 1. Obtain the repository

Clone the repository:

```powershell
git clone https://github.com/aliakbarse/GridSignal-AI.git
cd GridSignal-AI
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install the project and development dependencies

Run this command from the repository root:

```powershell
python -m pip install -e ".[dev]"
```

### 4. Download the source data

Download the required hourly day-ahead price and actual-generation CSV files from SMARD. Place them in `data/raw/` using the filenames expected by the scripts.

Check the applicable source terms before redistributing downloaded data.

### 5. Run the pipeline

Execute these commands from the repository root, in order:

```powershell
python -m gridsignal.inspect_data
python -m gridsignal.clean_data
python -m gridsignal.clean_generation
python -m gridsignal.combine_data
python -m gridsignal.analyze_prices
python -m gridsignal.plot_negative_price_frequency
python -m gridsignal.analyze_generation_by_price
python -m gridsignal.analyze_monthly_generation
python -m gridsignal.analyze_solar_consistency
python -m gridsignal.analyze_hour_of_day
python -m gridsignal.plot_negative_price_severity
python -m gridsignal.plot_monthly_solar_comparison
python -m gridsignal.plot_hour_of_day_analysis
```

Run the scripts from the repository root. The pipeline generates processed datasets under `data/processed/`, analytical summaries under `docs/`, and visualizations under `docs/`.

### 6. Run the tests

```powershell
python -m pytest -v
```

The current test suite contains nine tests covering key rules for negative-price classification, timestamp validation, and matching price and generation records. A passing test suite verifies the tested rules; it does not by itself validate every analytical conclusion.

## Planned Development

GridSignal AI is being developed incrementally.

1. **Market analytics:** Expand the analysis of price patterns, negative-price events, and renewable-generation relationships.
2. **Forecasting:** Develop baseline models and evaluate them against appropriate benchmarks.
3. **Evidence retrieval:** Retrieve relevant evidence from official energy-market and regulatory documents.
4. **AI orchestration:** Build a multi-step workflow using LangGraph to produce traceable answers.
5. **Evaluation:** Measure forecast accuracy, retrieval relevance, citation quality, and system performance.
6. **Application:** Expose the system through an API and introduce observability and further testing.

Potential technologies include pandas, DuckDB, Parquet, scikit-learn, LightGBM, PostgreSQL with pgvector, FastAPI, LangGraph, pytest, and Langfuse. These are planned components, not claims about implemented functionality.

## Guiding Principles

- Support analytical claims with measurable evidence.
- Preserve data provenance and document limitations.
- Compare forecasting models against appropriate baselines.
- Distinguish verified facts, model outputs, and uncertainty.
- Avoid presenting correlation as causation.
- Make analysis reproducible and results interpretable.

## License

A license has not yet been selected. The project's code and third-party data remain subject to their applicable terms until licensing and redistribution permissions are confirmed.
