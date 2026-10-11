with totals as (
 select 'monthly' as grain, sum(sales_value_gbp) as amount from {{ ref('mart_monthly_metrics') }}
 union all select 'country', sum(sales_value_gbp) from {{ ref('mart_country_sales') }}
 union all select 'stock_code', sum(sales_value_gbp) from {{ ref('mart_stock_code_sales') }}
 union all select 'customer_group', sum(sales_value_gbp) from {{ ref('mart_customer_group_sales') }}
), baseline as (
 select sum(sales_value_gbp) as amount from {{ ref('fct_sales_lines') }}
 where invoice_date >= date '2010-12-01' and invoice_date < date '2011-12-01'
)
select t.* from totals t cross join baseline b where t.amount is distinct from b.amount
