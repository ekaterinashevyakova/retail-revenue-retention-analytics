select * from {{ ref('mart_repeat_purchase') }}
where customers <= 0 or repeat_customers < 0 or repeat_customers > customers
   or repeat_purchase_rate < 0 or repeat_purchase_rate > 1
   or abs(repeat_purchase_rate - repeat_customers::numeric / nullif(customers,0)) > 1e-15
