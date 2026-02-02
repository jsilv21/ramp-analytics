with login_events as (
    select
        org_id,
        app_id,
        user_id,
        date_trunc('month', login_at) as month,
        count(*) as login_events
    from {{ ref('stg_okta_logins') }}
    group by 1, 2, 3, 4
),

usage_events as (
    select
        org_id,
        app_id,
        user_id,
        date_trunc('month', activity_at) as month,
        count(*) as usage_events,
        sum(duration_minutes) as usage_minutes
    from {{ ref('stg_saas_usage') }}
    group by 1, 2, 3, 4
),

combined as (
    select
        coalesce(login_events.org_id, usage_events.org_id) as org_id,
        coalesce(login_events.app_id, usage_events.app_id) as app_id,
        coalesce(login_events.user_id, usage_events.user_id) as user_id,
        coalesce(login_events.month, usage_events.month) as month,
        coalesce(login_events.login_events, 0) as login_events,
        coalesce(usage_events.usage_events, 0) as usage_events,
        coalesce(usage_events.usage_minutes, 0) as usage_minutes
    from login_events
    full outer join usage_events
        on login_events.org_id = usage_events.org_id
        and login_events.app_id = usage_events.app_id
        and login_events.user_id = usage_events.user_id
        and login_events.month = usage_events.month
)

select
    org_id,
    app_id,
    month,
    count(distinct user_id) as active_users,
    sum(login_events) as login_events,
    sum(usage_events) as usage_events,
    sum(usage_minutes) as usage_minutes
from combined
group by 1, 2, 3
