select invoice_no, customer_id, count(*)
from {{ ref('int_customer_orders') }}
group by 1, 2 having count(*) > 1
