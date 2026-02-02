{% set active_days = var('active_user_days', 60) %}

with reclaim as (
    select
        org_id,
        'reclaim_' || org_id || '_' || app_id || '_' || user_id as recommendation_id,
        'reclaim_inactive_user' as recommendation_type,
        recommendation_action as action,
        recommendation_reason as reason,
        'Last activity: ' || coalesce(cast(last_activity_at as varchar), 'never') as evidence,
        potential_savings as expected_savings,
        0.7 as confidence,
        app_id,
        app_name,
        user_id,
        email as user_email,
        category
    from {{ ref('mart_user_reclaim_candidates') }}
),

right_size as (
    select
        org_id,
        'right_size_' || org_id || '_' || app_id as recommendation_id,
        'right_size_app' as recommendation_type,
        'right_size_app' as action,
        'Utilization below cohort p25' as reason,
        'Utilization rate: ' || cast(utilization_rate as varchar) as evidence,
        rightsizing_opportunity as expected_savings,
        0.6 as confidence,
        app_id,
        app_name,
        null as user_id,
        null as user_email,
        category
    from {{ ref('mart_app_overview') }}
    where over_licensed_flag = true
        and rightsizing_opportunity is not null
        and rightsizing_opportunity > 0
),

spend_base as (
    select * from {{ ref('mart_spend_vs_usage') }}
),

latest as (
    select
        org_id,
        app_id,
        max(month) as latest_month
    from spend_base
    group by 1, 2
),

last_month as (
    select spend_base.*
    from spend_base
    inner join latest
        on spend_base.org_id = latest.org_id
        and spend_base.app_id = latest.app_id
        and spend_base.month = latest.latest_month
),

prior_window as (
    select
        spend_base.org_id,
        spend_base.app_id,
        avg(spend_base.total_amount) as prior_avg_spend,
        avg(spend_base.active_users) as prior_avg_active
    from spend_base
    inner join latest
        on spend_base.org_id = latest.org_id
        and spend_base.app_id = latest.app_id
    where spend_base.month < latest.latest_month
        and spend_base.month >= (latest.latest_month - interval '3 months')
    group by 1, 2
),

spend_spike as (
    select
        last_month.org_id,
        'spend_spike_' || last_month.org_id || '_' || last_month.app_id as recommendation_id,
        'investigate_spend_spike' as recommendation_type,
        'investigate_spend_spike' as action,
        'Spend increased with flat usage' as reason,
        'Last month spend: '
            || cast(last_month.total_amount as varchar)
            || ' vs prior avg: '
            || cast(prior_window.prior_avg_spend as varchar) as evidence,
        last_month.total_amount - prior_window.prior_avg_spend as expected_savings,
        0.5 as confidence,
        last_month.app_id,
        last_month.app_name,
        null as user_id,
        null as user_email,
        last_month.category
    from last_month
    inner join prior_window
        on last_month.org_id = prior_window.org_id
        and last_month.app_id = prior_window.app_id
    where prior_window.prior_avg_spend is not null
        and last_month.total_amount > prior_window.prior_avg_spend * 1.25
        and (
            prior_window.prior_avg_active is null
            or abs(last_month.active_users - prior_window.prior_avg_active)
                <= (prior_window.prior_avg_active * 0.1)
        )
),

low_util_apps as (
    select
        org_id,
        category,
        app_id,
        app_name,
        utilization_rate,
        rightsizing_opportunity
    from {{ ref('mart_app_overview') }}
    where cohort_utilization_p25 is not null
        and utilization_rate < cohort_utilization_p25
),

consolidate as (
    select
        org_id,
        category,
        string_agg(app_name, ', ') as app_list,
        count(*) as low_util_app_count,
        sum(rightsizing_opportunity) as total_rightsizing_opportunity
    from low_util_apps
    group by 1, 2
    having count(*) >= 2
)

select
    org_id,
    recommendation_id,
    recommendation_type,
    action,
    reason,
    evidence,
    expected_savings,
    confidence,
    app_id,
    app_name,
    user_id,
    user_email,
    category,
    current_timestamp as created_at
from reclaim

union all

select
    org_id,
    recommendation_id,
    recommendation_type,
    action,
    reason,
    evidence,
    expected_savings,
    confidence,
    app_id,
    app_name,
    user_id,
    user_email,
    category,
    current_timestamp as created_at
from right_size

union all

select
    org_id,
    recommendation_id,
    recommendation_type,
    action,
    reason,
    evidence,
    expected_savings,
    confidence,
    app_id,
    app_name,
    user_id,
    user_email,
    category,
    current_timestamp as created_at
from spend_spike

union all

select
    consolidate.org_id,
    'consolidate_' || consolidate.org_id || '_' || consolidate.category as recommendation_id,
    'consolidate_apps' as recommendation_type,
    'consolidate_apps' as action,
    'Multiple low-utilization apps in same category' as reason,
    'Apps: ' || consolidate.app_list as evidence,
    consolidate.total_rightsizing_opportunity as expected_savings,
    0.4 as confidence,
    null as app_id,
    null as app_name,
    null as user_id,
    null as user_email,
    consolidate.category,
    current_timestamp as created_at
from consolidate
