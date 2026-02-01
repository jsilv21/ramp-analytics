with source as (
    select * from {{ source('raw', 'raw_okta_logins') }}
)

select
    org_id,
    login_id,
    user_id,
    app_id,
    cast(login_ts as timestamp) as login_at,
    device,
    ip_address
from source
