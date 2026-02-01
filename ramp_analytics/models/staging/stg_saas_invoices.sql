with source as (
    select * from {{ source('raw', 'raw_saas_invoices') }}
)

select
    org_id,
    invoice_id,
    contract_id,
    app_id,
    cast(invoice_date as date) as invoice_date,
    cast(seats_billed as integer) as seats_billed,
    cast(total_amount as double) as total_amount,
    currency
from source
