with assignments as (
    select * from {{ ref('int_app_assignments') }}
),

activity as (
    select * from {{ ref('int_user_app_activity') }}
),

contracts as (
    select * from {{ ref('int_app_contracts_latest') }}
),

spend as (
    select * from {{ ref('int_app_spend_12m') }}
)

select
    assignments.org_id,
    assignments.app_id,
    count(distinct assignments.user_id) as assigned_seats,
    count(
        distinct case
            when activity.activity_status = 'active' then assignments.user_id
        end
    ) as active_seats,
    count(
        distinct case
            when coalesce(activity.activity_status, 'inactive') = 'inactive'
                then assignments.user_id
        end
    ) as inactive_seats,
    max(activity.last_activity_at) as last_activity_at,
    count(
        distinct case
            when activity.activity_status = 'active' then assignments.user_id
        end
    ) * 1.0
        / nullif(count(distinct assignments.user_id), 0) as utilization_rate,
    contracts.price_per_seat,
    contracts.min_seats,
    spend.total_spend_12m,
    spend.avg_monthly_spend_12m,
    spend.avg_seats_billed_12m,
    spend.currency as spend_currency,
    spend.total_spend_12m
        / nullif(
            count(
                distinct case
                    when activity.activity_status = 'active' then assignments.user_id
                end
            ),
            0
        ) as cost_per_active_seat
from assignments
left join activity
    on assignments.org_id = activity.org_id
    and assignments.app_id = activity.app_id
    and assignments.user_id = activity.user_id
left join contracts
    on assignments.org_id = contracts.org_id
    and assignments.app_id = contracts.app_id
left join spend
    on assignments.org_id = spend.org_id
    and assignments.app_id = spend.app_id
group by
    assignments.org_id,
    assignments.app_id,
    contracts.price_per_seat,
    contracts.min_seats,
    spend.total_spend_12m,
    spend.avg_monthly_spend_12m,
    spend.avg_seats_billed_12m,
    spend.currency
