{% set active_days = var('active_user_days', 60) %}

with assignments as (
    select * from {{ ref('int_app_assignments') }}
),

activity as (
    select * from {{ ref('int_user_app_activity') }}
),

apps as (
    select * from {{ ref('stg_okta_apps') }}
),

users as (
    select * from {{ ref('stg_okta_users') }}
),

contracts as (
    select * from {{ ref('int_app_contracts_latest') }}
)

select
    assignments.org_id,
    assignments.user_id,
    users.email,
    users.department,
    users.status,
    assignments.app_id,
    apps.app_name,
    apps.category,
    apps.vendor,
    activity.last_activity_at,
    activity.inactivity_days,
    case
        when activity.last_activity_at is null then 'never_used'
        else 'inactive'
    end as inactivity_reason,
    contracts.price_per_seat,
    'reclaim_seat' as recommendation_action,
    contracts.price_per_seat as potential_savings,
    'No activity in last {{ active_days }} days' as recommendation_reason
from assignments
left join activity
    on assignments.org_id = activity.org_id
    and assignments.app_id = activity.app_id
    and assignments.user_id = activity.user_id
left join users
    on assignments.org_id = users.org_id
    and assignments.user_id = users.user_id
left join apps
    on assignments.org_id = apps.org_id
    and assignments.app_id = apps.app_id
left join contracts
    on assignments.org_id = contracts.org_id
    and assignments.app_id = contracts.app_id
where coalesce(activity.activity_status, 'inactive') = 'inactive'
