## Local dbt profile

This repo uses a project-local dbt profile so setup is self-serve.

Run dbt with:

```bash
uv run dbt --profiles-dir config debug
uv run dbt --profiles-dir config run
```
