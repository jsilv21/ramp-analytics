from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

DEFAULT_DB_PATH = Path("../warehouse/ramp.duckdb")


def get_db_path() -> Path:
    env_path = os.getenv("RAMP_DUCKDB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


@st.cache_data(ttl=300)
def load_app_overview(db_path: Path) -> pd.DataFrame:
    with duckdb.connect(str(db_path)) as conn:
        return conn.execute(
            """
            select
              org_id,
              org_name,
              industry,
              employee_band,
              region,
              app_id,
              app_name,
              category,
              vendor,
              assigned_seats,
              active_seats,
              inactive_seats,
              utilization_rate,
              total_spend_12m,
              avg_monthly_spend_12m,
              cost_per_active_seat,
              rightsizing_opportunity,
              over_licensed_flag
            from analytics.mart_app_overview
            """
        ).df()


@st.cache_data(ttl=300)
def load_spend_vs_usage(db_path: Path) -> pd.DataFrame:
    with duckdb.connect(str(db_path)) as conn:
        return conn.execute(
            """
            select
              month,
              org_id,
              org_name,
              app_id,
              app_name,
              category,
              total_amount,
              active_users
            from analytics.mart_spend_vs_usage
            """
        ).df()


def apply_filters(df: pd.DataFrame, org: str, app: str, category: str) -> pd.DataFrame:
    filtered = df
    if org != "All":
        filtered = filtered[filtered["org_name"] == org]
    if app != "All":
        filtered = filtered[filtered["app_name"] == app]
    if category != "All":
        filtered = filtered[filtered["category"] == category]
    return filtered


def main() -> None:
    st.set_page_config(page_title="Seat Intelligence", layout="wide")
    st.title("Seat Intelligence Overview")

    db_path = get_db_path()
    if not db_path.exists():
        st.error(
            f"DuckDB file not found: {db_path}. "
            "Run dbt to build models or set RAMP_DUCKDB_PATH."
        )
        return

    try:
        app_overview = load_app_overview(db_path)
        spend_vs_usage = load_spend_vs_usage(db_path)
    except Exception as exc:  # pragma: no cover - surface to UI
        st.error(f"Failed to load data: {exc}")
        return

    if app_overview.empty:
        st.warning("No rows found in analytics.mart_app_overview.")
        return

    st.sidebar.header("Filters")
    org_options = ["All"] + sorted(app_overview["org_name"].dropna().unique().tolist())
    app_options = ["All"] + sorted(app_overview["app_name"].dropna().unique().tolist())
    category_options = ["All"] + sorted(
        app_overview["category"].dropna().unique().tolist()
    )

    selected_org = st.sidebar.selectbox("Organization", org_options)
    selected_app = st.sidebar.selectbox("Application", app_options)
    selected_category = st.sidebar.selectbox("Category", category_options)

    filtered_overview = apply_filters(
        app_overview, selected_org, selected_app, selected_category
    )
    filtered_spend = apply_filters(
        spend_vs_usage, selected_org, selected_app, selected_category
    )

    total_spend = filtered_overview["total_spend_12m"].sum()
    avg_utilization = filtered_overview["utilization_rate"].mean()
    inactive_seats = filtered_overview["inactive_seats"].sum()
    rightsizing = filtered_overview["rightsizing_opportunity"].sum()

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Spend (12m)", f"${total_spend:,.0f}")
    kpi_cols[1].metric(
        "Avg Utilization",
        f"{avg_utilization:.1%}" if pd.notna(avg_utilization) else "—",
    )
    kpi_cols[2].metric("Inactive Seats", f"{inactive_seats:,.0f}")
    kpi_cols[3].metric("Rightsizing Opportunity", f"${rightsizing:,.0f}")

    st.subheader("Top Rightsizing Opportunities")
    top_rightsizing = (
        filtered_overview.dropna(subset=["rightsizing_opportunity"])
        .sort_values("rightsizing_opportunity", ascending=False)
        .head(10)
    )
    top_rightsizing_display = top_rightsizing.copy()
    top_rightsizing_display["utilization_rate"] = (
        top_rightsizing_display["utilization_rate"] * 100
    ).round(1).astype(str) + "%"
    top_rightsizing_display["rightsizing_opportunity"] = (
        top_rightsizing_display["rightsizing_opportunity"]
        .fillna(0)
        .map(lambda value: f"${value:,.0f}")
    )
    st.dataframe(
        top_rightsizing_display[
            [
                "org_name",
                "app_name",
                "category",
                "inactive_seats",
                "utilization_rate",
                "rightsizing_opportunity",
            ]
        ],
        use_container_width=True,
    )

    st.subheader("Spend vs Active Usage (Monthly)")
    if filtered_spend.empty:
        st.info("No spend data available for the selected filters.")
    else:
        trend = (
            filtered_spend.groupby("month", as_index=False)
            .agg(
                total_amount=("total_amount", "sum"),
                active_users=("active_users", "sum"),
            )
            .sort_values("month")
        )
        st.line_chart(trend.set_index("month")[["total_amount", "active_users"]])

    st.subheader("App Overview (Filtered)")
    overview_display = filtered_overview.copy()
    overview_display["utilization_rate"] = (
        overview_display["utilization_rate"] * 100
    ).round(1).astype(str) + "%"
    overview_display["total_spend_12m"] = (
        overview_display["total_spend_12m"]
        .fillna(0)
        .map(lambda value: f"${value:,.0f}")
    )
    overview_display["cost_per_active_seat"] = (
        overview_display["cost_per_active_seat"]
        .fillna(0)
        .map(lambda value: f"${value:,.0f}")
    )
    st.dataframe(
        overview_display[
            [
                "org_name",
                "app_name",
                "category",
                "assigned_seats",
                "active_seats",
                "inactive_seats",
                "utilization_rate",
                "total_spend_12m",
                "cost_per_active_seat",
                "over_licensed_flag",
            ]
        ],
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
