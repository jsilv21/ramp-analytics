with contracts as (
    select * from {{ ref('stg_saas_contracts') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by org_id, app_id
            order by start_date desc, end_date desc
        ) as row_num
    from contracts
)

select
    org_id,
    contract_id,
    app_id,
    app_key,
    start_date,
    end_date,
    term_months,
    price_per_seat,
    min_seats,
    billing_frequency,
    currency
from ranked
where row_num = 1
