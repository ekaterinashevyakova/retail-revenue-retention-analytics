select invoice_no, customer_id, min(invoice_date) as order_date,
       sum(sales_value_gbp) as sales_value_gbp
from {{ ref('fct_sales_lines') }}
where has_customer_id
group by invoice_no, customer_id
