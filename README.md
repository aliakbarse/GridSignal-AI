# GridSignal AI

**An evidence-grounded intelligence assistant for the German electricity market.**

GridSignal AI is a portfolio project exploring how electricity-market analytics, forecasting, and retrieval-augmented generation (RAG) can work together to explain market conditions using quantitative data and traceable evidence.

The project begins with a reproducible Python data pipeline analyzing German day-ahead electricity prices and selected renewable-generation data for 2024–2025. Future development will introduce forecasting, evidence retrieval, and AI-assisted explanations.

## Research Question

How did negative electricity prices vary across months in 2024 and 2025, and how did wind and solar generation differ between negative-price and nonnegative-price hours?

## Key Findings

### 1. Negative prices became more frequent in May and June 2025

| Month | Negative-price hours in 2024 | Frequency in 2024 | Negative-price hours in 2025 | Frequency in 2025 |
|---|---:|---:|---:|---:|
| May | 78 | 10.48% | 129 | 17.34% |
| June | 64 | 8.89% | 141 | 19.58% |

June 2025 had the highest observed monthly negative-price frequency in the dataset: **19.58% of observed hours**.

The frequency fell to 1.61% in July 2025. These month-to-month changes identify periods worth investigating further, but do not explain their underlying causes.

### 2. Solar generation was higher during negative-price hours

In May 2025, average solar generation was approximately 34,775 MWh during negative-price hours, compared with 9,415 MWh during nonnegative-price hours.

In June 2025, the corresponding averages were approximately 35,296 MWh and 9,713 MWh.

These values represent average generation per hourly interval, not monthly generation totals. The observed association does not establish causation. Demand, conventional generation, electricity imports and exports, storage, and other market conditions may also influence prices.

### 3. The data pipeline validates the joined dataset

The analysis combines **17,541 hourly price records with 17,541 matching generation records** for 2024–2025.

The validation logic checks for missing timestamps, duplicate timestamps, and unmatched intervals before the datasets are combined. The current automated test suite contains seven passing tests covering key price-classification and data-joining rules.

## Visualization

![Monthly frequency of negative electricity prices in Germany, 2024–2025](docs/negative_price_frequency_2024_2025.png)

*Monthly share of observed hours with day-ahead prices below €0/MWh. Source: SMARD. The final three hours of 2025 are absent from the downloaded source data.*

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
- Price and generation records are joined using UTC timestamps.
- German local time (`Europe/Berlin`) is used for calendar-year and monthly analysis.
- Daylight-saving transitions mean that local months can contain different numbers of hours.
- Negative-price frequency is calculated using the number of observed hourly records.
- Months with no negative-price hours cannot support a comparison between negative-price and nonnegative-price hours.
- The analysis is descriptive and does not establish causal relationships.

The pipeline uses the source's reported generation values. Some electricity-generation data published through SMARD may include estimates where actual measurements are incomplete.

## Methodology

The current workflow follows these stages:

1. **Inspect:** Examine source files, columns, timestamp formats, and data quality.
2. **Clean:** Parse timestamps and numerical values, handle missing data, and convert German local timestamps to UTC.
3. **Validate:** Check timestamp uniqueness and ensure price and generation intervals match.
4. **Combine:** Join prices and selected generation measures using UTC timestamps.
5. **Analyze:** Calculate monthly negative-price frequency and compare average generation across price categories.
6. **Visualize:** Produce a monthly negative-price frequency chart for the portfolio.

The results are generated locally from downloaded source files using Python and pandas.

## Repository Structure

```text
GridSignal_AI/
├── data/
│   ├── raw/                       # Original source files (local)
│   └── processed/                 # Generated datasets (local)
├── docs/
│   ├── findings.md                # Written analytical findings
│   └── negative_price_frequency_2024_2025.png
├── src/
│   └── gridsignal/
│       ├── inspect_data.py
│       ├── clean_data.py
│       ├── clean_generation.py
│       ├── data_validation.py
│       ├── combine_data.py
│       ├── analyze_prices.py
│       └── plot_negative_price_frequency.py
├── tests/
│   └── test_data_pipeline.py
├── .gitignore
├── pyproject.toml
└── README.md
```

Raw and processed datasets are excluded from version control. The chart and written findings are intended to be included in the repository.

## Run the Project Locally

### Requirements

- Python 3.14 or later, as specified in the current project configuration
- pip
- Git (optional)

### 1. Obtain the repository

After the project is published, clone it using your repository URL:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd 02_GridSignal_AI
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
```

The scripts generate processed datasets under `data/processed/` and save the visualization under `docs/`.

### 6. Run the tests

```powershell
python -m pytest -v
```

The current test suite checks key rules for negative-price classification, timestamp validation, and matching price and generation records.

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
