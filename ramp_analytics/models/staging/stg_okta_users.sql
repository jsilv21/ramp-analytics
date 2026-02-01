with source as (
    select * from {{ source('raw', 'raw_okta_users') }}
)

select
    org_id,
    user_id,
    first_name,
    last_name,
    email,
    department,
    title,
    status,
    cast(is_admin as boolean) as is_admin,
    cast(created_at as timestamp) as created_at,
    cast(last_login_at as timestamp) as last_login_at
from source
