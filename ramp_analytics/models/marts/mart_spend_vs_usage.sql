with spend as (
    select * from {{ ref('int_app_spend_monthly') }}
),

activity as (
    select * from {{ ref('int_app_monthly_activity') }}
),

app_metrics as (
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
    spend.org_id,
    orgs.org_name,
    orgs.industry,
    orgs.employee_band,
    orgs.region,
    spend.app_id,
    apps.app_name,
    apps.category,
    apps.vendor,
    spend.month,
    spend.total_amount,
    spend.seats_billed,
    spend.currency,
    coalesce(activity.active_users, 0) as active_users,
    coalesce(activity.login_events, 0) as login_events,
    coalesce(activity.usage_events, 0) as usage_events,
    coalesce(activity.usage_minutes, 0) as usage_minutes,
    app_metrics.assigned_seats,
    coalesce(activity.active_users, 0) * 1.0
        / nullif(app_metrics.assigned_seats, 0) as utilization_rate_month,
    spend.total_amount / nullif(coalesce(activity.active_users, 0), 0) as cost_per_active_seat_month,
    benchmarks.utilization_p50 as cohort_utilization_p50,
    (coalesce(activity.active_users, 0) * 1.0 / nullif(app_metrics.assigned_seats, 0))
        / nullif(benchmarks.utilization_p50, 0) as efficiency_score
from spend
left join activity
    on spend.org_id = activity.org_id
    and spend.app_id = activity.app_id
    and spend.month = activity.month
left join app_metrics
    on spend.org_id = app_metrics.org_id
    and spend.app_id = app_metrics.app_id
left join apps
    on spend.org_id = apps.org_id
    and spend.app_id = apps.app_id
left join orgs
    on spend.org_id = orgs.org_id
left join benchmarks
    on orgs.industry = benchmarks.industry
    and orgs.employee_band = benchmarks.employee_band
    and orgs.region = benchmarks.region
