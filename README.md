# GridSignal AI

**An evidence-grounded intelligence assistant for the German electricity market.**

GridSignal AI is a portfolio project exploring how electricity-market analytics, forecasting, and retrieval-augmented generation (RAG) can work together to explain market conditions using quantitative data and traceable evidence.

The project is being developed incrementally, starting with reproducible analysis of German day-ahead electricity prices and renewable generation.

## Current Results

The initial analysis covers German day-ahead electricity prices and selected electricity-generation sources for 2024–2025, using hourly data from SMARD.

The first analysis investigates how frequently electricity prices fall below €0/MWh and how those events relate to wind and solar generation.

### Initial Findings

- Negative-price frequency varied substantially by month.
- June 2025 had the highest observed monthly frequency in the dataset: approximately 19.6% of observed hours.
- Negative-price frequency dropped to approximately 1.6% in July 2025.
- Average solar generation was higher during negative-price hours in many spring and summer months. This is an observed association, not proof of causation.
- Wind-generation differences varied by month and require further investigation.

These findings are descriptive. They do not establish that renewable generation alone caused negative electricity prices.

### First Visualization

![Monthly frequency of negative electricity prices in Germany, 2024–2025](docs/negative_price_frequency_2024_2025.png)

*Monthly share of observed hours with day-ahead prices below €0/MWh. Source: SMARD. Percentages use the available hourly observations.*

## Data Sources and Limitations

**Primary source:** [SMARD — Germany's electricity market data platform](https://www.smard.de/en)

The project uses hourly data for the Germany/Luxembourg bidding zone, including:

- Day-ahead electricity prices (€/MWh)
- Actual offshore and onshore wind generation
- Actual solar generation

The selected generation measures do not represent total electricity supply or all renewable sources.

### Data Quality

- All 8,784 hours of the 2024 leap year are present.
- The 2025 dataset contains 8,757 hourly records. The final three hours of the year are missing from the downloaded source data.
- Price and generation records are joined using UTC timestamps.
- German local time (`Europe/Berlin`) is used for calendar-year and monthly analysis.
- Daylight-saving transitions mean local months can contain 23-hour or 25-hour days.
- Negative-price frequency is calculated using observed hours, allowing comparisons between months with different numbers of hours.

Data preparation, timestamp handling, joining, and validation are implemented in the project's Python scripts.

## Repository Structure

```text
GridSignal_AI/
├── data/
│   ├── raw/                 # Original downloaded data (local)
│   └── processed/           # Intermediate datasets (local)
├── docs/
│   └── negative_price_frequency_2024_2025.png
├── src/
│   └── gridsignal/
│       ├── inspect_data.py
│       ├── clean_data.py
│       ├── clean_generation.py
│       ├── combine_data.py
│       ├── analyze_prices.py
│       └── plot_negative_price_frequency.py
├── .gitignore
├── pyproject.toml
└── README.md
```

Raw and processed data directories are excluded from version control. The visualization in `docs/` is included so that it can be displayed directly in the GitHub README.

To reproduce the analysis, download the relevant source CSV files from SMARD and place them in `data/raw/` using the filenames expected by the scripts. Check the applicable source terms before redistributing any downloaded data.

## Run the Analysis Locally

### Requirements

- Python 3.14 or later, consistent with the current project configuration
- pip
- Git (optional, for cloning the repository)

### 1. Clone the repository

After the project is published, replace the placeholder with its GitHub repository URL.

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd 02_GridSignal_AI
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install the project and dependencies

Run this command from the repository root:

```powershell
python -m pip install -e .
```

### 4. Download the source data

Download the hourly day-ahead price and actual-generation CSV files from SMARD. Place them in `data/raw/` using the filenames expected by the scripts.

### 5. Run the pipeline

Run these commands from the repository root, in order:

```powershell
python src/gridsignal/inspect_data.py
python src/gridsignal/clean_data.py
python src/gridsignal/clean_generation.py
python src/gridsignal/combine_data.py
python src/gridsignal/analyze_prices.py
python src/gridsignal/plot_negative_price_frequency.py
```

The scripts create processed datasets under `data/processed/` and save the final visualization under `docs/`.

## Planned Development

The project will expand in stages:

1. **Market analytics:** Explore price patterns, negative-price events, and renewable-generation relationships.
2. **Forecasting:** Develop baseline models and evaluate them against appropriate benchmarks.
3. **Evidence retrieval:** Retrieve relevant evidence from official energy-market and regulatory documents.
4. **AI orchestration:** Build a multi-step workflow using LangGraph to produce traceable answers.
5. **Evaluation:** Measure forecast accuracy, retrieval relevance, citation quality, and system performance.
6. **Application:** Expose the system through an API and add observability and testing.

Potential technologies include pandas, DuckDB, Parquet, scikit-learn, LightGBM, PostgreSQL with pgvector, FastAPI, LangGraph, pytest, and Langfuse. These are planned components; they are not all implemented yet.

## Guiding Principles

- Support analytical claims with measurable data.
- Preserve data provenance and document limitations.
- Compare forecasting models against appropriate baselines.
- Distinguish verified facts, model outputs, and uncertainty.
- Avoid presenting correlation as causation.
- Make analysis reproducible and results interpretable.

## License

A license has not yet been selected. The project's code and third-party data remain subject to their applicable terms until licensing and redistribution permissions are confirmed.