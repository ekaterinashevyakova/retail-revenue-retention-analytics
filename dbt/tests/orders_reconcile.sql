with baseline as (
 select count(distinct invoice_no) as orders from {{ ref('fct_sales_lines') }}
 where invoice_date >= date '2010-12-01' and invoice_date < date '2011-12-01'
)
select sum(m.orders) as monthly_orders from {{ ref('mart_monthly_metrics') }} m
cross join baseline b group by b.orders having sum(m.orders) <> b.orders
