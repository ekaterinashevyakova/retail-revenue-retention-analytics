select month, customer_group, count(*)
from {{ ref('mart_customer_group_sales') }}
group by 1, 2 having count(*) > 1
