with invoices as (
    select * from {{ ref('stg_saas_invoices') }}
)

select
    org_id,
    app_id,
    date_trunc('month', invoice_date) as month,
    sum(total_amount) as total_amount,
    sum(seats_billed) as seats_billed,
    max(currency) as currency
from invoices
group by 1, 2, 3
