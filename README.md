## Local dbt profile

This repo uses a project-local dbt profile so setup is self-serve.

Generate synthetic data (first-time setup):

```bash
uv run python scripts/generate_synthetic_data.py
uv run python scripts/ingest_raw_to_duckdb.py
```

Run dbt with:

```bash
uv run dbt --profiles-dir config debug
uv run dbt --profiles-dir config run
```
