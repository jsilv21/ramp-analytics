with monthly as (
    select * from {{ ref('int_app_spend_monthly') }}
)

select
    org_id,
    app_id,
    sum(total_amount) as total_spend_12m,
    avg(total_amount) as avg_monthly_spend_12m,
    avg(seats_billed) as avg_seats_billed_12m,
    max(currency) as currency
from monthly
where month >= (date_trunc('month', current_date) - interval '11 months')
group by 1, 2
