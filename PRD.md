# PRD: Seat Intelligence (Okta + SaaS Spend)

## Overview
Seat Intelligence connects Okta identity data with SaaS spend to surface usage trends, identify inactive users, and benchmark cost efficiency. It outputs clear, explainable recommendations to reduce software waste and improve license allocation.

## Goals
- Quantify seat utilization and reclaim/downgrade opportunities.
- Provide explainable recommendations with estimated savings.
- Benchmark spend efficiency and utilization vs peers.
- Deliver decision-ready marts and dashboards.

## Non-Goals
- Real-time license enforcement.
- Full identity governance workflows.
- Proprietary vendor pricing modeling.

## Target Users & Use Cases
- Finance/IT leaders: reclaim inactive users, right-size apps, negotiate renewals.
- Procurement: compare spend efficiency to peer cohorts.
- SaaS admins: monitor usage trends and prevent waste creep.

## Synthetic Data Inputs
- Okta: users, groups, apps, assignments, login events
- SaaS spend: contracts, invoices, billed seats, price per seat
- Org metadata: industry, size band, region

## Synthetic Data Scope (Generator Defaults)
- Orgs: 12 orgs, 120–800 employees each
- Orgs created: within last ~5 years
- Users created: between org creation and ~1 week ago
- Activity/logins: concentrated in last 90 days (active users within last 30 days)
- Spend/invoices: monthly invoices for last 12 months

## Outputs (Data Marts)
- `mart_app_overview` (app KPIs)
- `mart_user_reclaim_candidates` (inactive users + impact)
- `mart_spend_vs_usage` (trend + efficiency score)
- `mart_recommendations` (action, reason, savings)
- `mart_benchmarks` (cohort percentiles)

## Core Metrics (MVP)
- Active user: login/usage within last 60 days (configurable via dbt `active_user_days` var or model default)
- Utilization rate = active_seats / assigned_seats
- Cost per active seat = total_cost / active_seats
- Over-licensed flag = utilization_rate < cohort p25
- Rightsize opportunity = (assigned_seats - active_seats) * price_per_seat

## Recommendation Logic (MVP)
- Reclaim inactive users (no login in 60 days).
- Right-size apps below cohort p25 utilization.
- Investigate spend spikes with flat usage.
- Consolidate low-utilization apps in same category.

Each recommendation includes action, evidence, expected savings, confidence.

## Benchmarks
Cohorts by industry, employee size band, region. Report p25/p50/p75 for utilization and spend per active seat.

## Technical Decisions
- Warehouse: DuckDB (local, zero infra)
- Modeling: dbt Core only (avoid dbt Fusion conflicts with DuckDB)
- Runtime: Python 3.13
- Front end: Evidence.dev dashboards

## Risks
- Usage proxy may misrepresent product engagement (mitigate with usage events).
- Sparse login data for some apps (supplement with app usage).

## Milestones
- M1: Synthetic data generator + raw tables
- M2: dbt staging + tests
- M3: Marts + recommendations + benchmarks
- M4: Evidence.dev dashboards
- M5: Documentation + demo narrative
