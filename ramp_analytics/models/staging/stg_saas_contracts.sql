with source as (
    select * from {{ source('raw', 'raw_saas_contracts') }}
)

select
    org_id,
    contract_id,
    app_id,
    app_key,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date,
    cast(term_months as integer) as term_months,
    cast(price_per_seat as double) as price_per_seat,
    cast(min_seats as integer) as min_seats,
    billing_frequency,
    currency
from source
