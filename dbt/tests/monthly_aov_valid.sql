select * from {{ ref('mart_monthly_metrics') }}
where orders <= 0 or sales_value_gbp <= 0 or cancellation_value_gbp < 0
   or average_order_value_gbp is null
   or abs(average_order_value_gbp - sales_value_gbp / nullif(orders,0)) > 1e-16
