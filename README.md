# GridSignal AI

**An evidence-grounded intelligence assistant for the German electricity market.**

GridSignal AI is a portfolio project exploring how market data, forecasting, and retrieval-augmented generation (RAG) can work together to explain electricity-market conditions using quantitative evidence and official sources.

## Project Goals

- Analyze German electricity-market data.
- Investigate electricity-price patterns and negative-price events.
- Develop and evaluate baseline forecasting models.
- Retrieve relevant evidence from official energy-market and regulatory documents.
- Build a multi-step AI workflow that produces traceable, evidence-backed answers.
- Evaluate forecast accuracy, retrieval quality, citation quality, and system performance.

## Planned Technology Stack

- **Language:** Python
- **Data analysis:** pandas, DuckDB, Parquet
- **Machine learning:** scikit-learn and LightGBM
- **AI orchestration:** LangGraph
- **Retrieval:** Embeddings, RAG, PostgreSQL with pgvector
- **API:** FastAPI
- **Testing and evaluation:** pytest and custom evaluation metrics
- **Observability:** Langfuse
- **Version control:** Git

## Development Status

**Current stage:** Project foundation.

The Python package structure, virtual environment, initial configuration, and first executable script have been created.

Data ingestion, forecasting, retrieval, evaluation, and application components are planned future milestones and have not yet been implemented.

## Guiding Principle

Market explanations should be supported by measurable data and traceable evidence. Forecasts will be evaluated against baselines, and generated answers should distinguish verified facts from uncertainty.

## License

License to be determined.