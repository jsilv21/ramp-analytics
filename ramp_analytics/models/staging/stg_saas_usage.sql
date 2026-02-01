with source as (
    select * from {{ source('raw', 'raw_saas_usage') }}
)

select
    org_id,
    usage_id,
    user_id,
    app_id,
    cast(activity_ts as timestamp) as activity_at,
    activity_type,
    cast(duration_minutes as integer) as duration_minutes
from source
