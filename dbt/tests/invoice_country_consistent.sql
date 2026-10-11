select invoice_no, count(distinct country)
from {{ ref('fct_sales_lines') }}
where invoice_date >= date '2010-12-01' and invoice_date < date '2011-12-01'
group by 1 having count(distinct country) > 1
