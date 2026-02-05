-- 1) Row count
select count(*) from {{ref("stg_saas_invoices")}}

-- -- 2) Date range
-- select min(invoice_date), max(invoice_date) from stg_saas_invoices;

-- -- 3) Key uniqueness
-- select
--   count(*) as rows,
--   count(distinct invoice_id) as distinct_ids
-- from stg_saas_invoices;

-- -- 4) Null rates (pick key fields)
-- select
--   sum(case when org_id is null then 1 else 0 end) as org_id_nulls,
--   sum(case when app_id is null then 1 else 0 end) as app_id_nulls
-- from stg_saas_invoices;

-- -- 5) Small sample
-- select * from stg_saas_invoices limit 20;
