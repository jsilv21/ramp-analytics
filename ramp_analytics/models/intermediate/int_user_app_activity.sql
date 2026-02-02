{% set active_days = var('active_user_days', 60) %}

with logins as (
    select
        org_id,
        app_id,
        user_id,
        max(login_at) as last_login_at,
        count(*) as login_events
    from {{ ref('stg_okta_logins') }}
    group by 1, 2, 3
),

usage as (
    select
        org_id,
        app_id,
        user_id,
        max(activity_at) as last_usage_at,
        count(*) as usage_events,
        sum(duration_minutes) as usage_minutes
    from {{ ref('stg_saas_usage') }}
    group by 1, 2, 3
),

users as (
    select
        org_id,
        user_id,
        status,
        department,
        last_login_at as user_last_login_at
    from {{ ref('stg_okta_users') }}
)

select
    coalesce(logins.org_id, usage.org_id) as org_id,
    coalesce(logins.app_id, usage.app_id) as app_id,
    coalesce(logins.user_id, usage.user_id) as user_id,
    users.status,
    users.department,
    logins.last_login_at,
    usage.last_usage_at,
    users.user_last_login_at,
    greatest(logins.last_login_at, usage.last_usage_at) as last_activity_at,
    coalesce(logins.login_events, 0) as login_events,
    coalesce(usage.usage_events, 0) as usage_events,
    coalesce(usage.usage_minutes, 0) as usage_minutes,
    case
        when greatest(logins.last_login_at, usage.last_usage_at) is null then 'inactive'
        when greatest(logins.last_login_at, usage.last_usage_at)
            >= (current_timestamp - interval '{{ active_days }} day') then 'active'
        else 'inactive'
    end as activity_status,
    case
        when greatest(logins.last_login_at, usage.last_usage_at) is null then null
        else date_diff(
            'day',
            greatest(logins.last_login_at, usage.last_usage_at),
            current_timestamp
        )
    end as inactivity_days
from logins
full outer join usage
    on logins.org_id = usage.org_id
    and logins.app_id = usage.app_id
    and logins.user_id = usage.user_id
left join users
    on users.org_id = coalesce(logins.org_id, usage.org_id)
    and users.user_id = coalesce(logins.user_id, usage.user_id)
