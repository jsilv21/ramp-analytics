## Local dbt profile

This repo uses a project-local dbt profile so setup is self-serve.

Generate synthetic data (first-time setup):

```bash
uv run python scripts/generate_synthetic_data.py
uv run python scripts/ingest_raw_to_duckdb.py
```

Run dbt with:

```bash
uv run dbt --project-dir ramp_analytics debug
uv run dbt --project-dir ramp_analytics deps
uv run dbt --project-dir ramp_analytics build
```

## Streamlit (frontend)

Streamlit runs in a separate uv project to avoid dependency conflicts with dbt.

Setup and run:

```bash
cd frontend
uv sync
uv run streamlit run ../streamlit_app.py
```

Optional: point Streamlit at a different DuckDB file:

```bash
RAMP_DUCKDB_PATH=path/to/ramp.duckdb uv run streamlit run ../streamlit_app.py
```
