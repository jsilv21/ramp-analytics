with source as (
    select * from {{ source('raw', 'raw_okta_apps') }}
)

select
    org_id,
    app_id,
    app_key,
    app_name,
    category,
    vendor,
    cast(enabled_at as timestamp) as enabled_at,
    cast(base_price as double) as base_price,
    cast(core as boolean) as is_core,
    cast(core_app as boolean) as is_core_app,
    target_departments
from source
