with source as (
    select * from {{ source('raw', 'raw_orgs') }}
)

select
    org_id,
    org_name,
    industry,
    cast(employee_count as integer) as employee_count,
    employee_band,
    region,
    cast(created_at as timestamp) as created_at
from source
