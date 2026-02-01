with source as (
    select * from {{ source('raw', 'raw_okta_groups') }}
)

select
    org_id,
    group_id,
    group_name,
    department
from source
