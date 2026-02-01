with source as (
    select * from {{ source('raw', 'raw_okta_assignments') }}
)

select
    org_id,
    assignment_id,
    user_id,
    app_id,
    cast(assigned_at as timestamp) as assigned_at,
    assigned_by
from source
