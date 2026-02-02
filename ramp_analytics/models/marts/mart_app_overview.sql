with app_metrics as (
    select * from {{ ref('int_app_metrics') }}
),

apps as (
    select * from {{ ref('stg_okta_apps') }}
),

orgs as (
    select * from {{ ref('stg_orgs') }}
),

benchmarks as (
    select * from {{ ref('mart_benchmarks') }}
)

select
    app_metrics.org_id,
    orgs.org_name,
    orgs.industry,
    orgs.employee_band,
    orgs.region,
    app_metrics.app_id,
    apps.app_key,
    apps.app_name,
    apps.category,
    apps.vendor,
    app_metrics.assigned_seats,
    app_metrics.active_seats,
    app_metrics.inactive_seats,
    app_metrics.utilization_rate,
    app_metrics.price_per_seat,
    app_metrics.min_seats,
    app_metrics.total_spend_12m,
    app_metrics.avg_monthly_spend_12m,
    app_metrics.cost_per_active_seat,
    app_metrics.last_activity_at,
    benchmarks.utilization_p25 as cohort_utilization_p25,
    benchmarks.utilization_p50 as cohort_utilization_p50,
    benchmarks.utilization_p75 as cohort_utilization_p75,
    case
        when benchmarks.utilization_p25 is null then false
        when app_metrics.utilization_rate < benchmarks.utilization_p25 then true
        else false
    end as over_licensed_flag,
    case
        when app_metrics.price_per_seat is null then null
        else greatest(app_metrics.assigned_seats - app_metrics.active_seats, 0)
            * app_metrics.price_per_seat
    end as rightsizing_opportunity
from app_metrics
left join apps
    on app_metrics.org_id = apps.org_id
    and app_metrics.app_id = apps.app_id
left join orgs
    on app_metrics.org_id = orgs.org_id
left join benchmarks
    on orgs.industry = benchmarks.industry
    and orgs.employee_band = benchmarks.employee_band
    and orgs.region = benchmarks.region
