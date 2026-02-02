with app_metrics as (
    select * from {{ ref('int_app_metrics') }}
),

orgs as (
    select * from {{ ref('stg_orgs') }}
)

select
    orgs.industry,
    orgs.employee_band,
    orgs.region,
    count(*) as app_count,
    count(distinct app_metrics.org_id) as org_count,
    quantile_cont(app_metrics.utilization_rate, 0.25) as utilization_p25,
    quantile_cont(app_metrics.utilization_rate, 0.5) as utilization_p50,
    quantile_cont(app_metrics.utilization_rate, 0.75) as utilization_p75,
    quantile_cont(app_metrics.cost_per_active_seat, 0.25) as cost_per_active_seat_p25,
    quantile_cont(app_metrics.cost_per_active_seat, 0.5) as cost_per_active_seat_p50,
    quantile_cont(app_metrics.cost_per_active_seat, 0.75) as cost_per_active_seat_p75
from app_metrics
left join orgs
    on app_metrics.org_id = orgs.org_id
where app_metrics.utilization_rate is not null
group by 1, 2, 3
