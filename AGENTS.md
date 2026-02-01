# AGENTS.md

## Guiding Principles (LLM Context)
- Build a demo-able Seat Intelligence product: Okta usage + SaaS spend -> actionable recommendations.
- Optimize for local, zero-infra setup so a Ramp teammate can run it easily.
- Technical decisions are locked:
  - DuckDB as the warehouse.
  - dbt Core only (avoid dbt Fusion with DuckDB).
  - Python 3.13 runtime.
  - Use uv for Python dependency management.
  - Evidence.dev for dashboards.
- Data outputs must be decision-ready marts with clear, explainable metrics and recommendations.
- Favor clarity and realism in synthetic data (usage patterns, inactivity, spend/seat).
- Always include dbt tests + documentation for models and metrics.
- Keep scope focused: MVP insights > extra features.
