with assignments as (
    select * from {{ ref('stg_okta_assignments') }}
)

select
    org_id,
    app_id,
    user_id,
    min(assigned_at) as first_assigned_at,
    max(assigned_at) as last_assigned_at
from assignments
group by 1, 2, 3
