WITH customer_counts AS (
    SELECT customer_id, COUNT(DISTINCT invoice_no) AS orders
    FROM {{ ref('int_customer_orders') }}
    WHERE order_date >= DATE '2010-12-01' AND order_date < DATE '2011-12-01'
    GROUP BY customer_id
)
SELECT COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE orders >= 2) AS repeat_customers,
       (COUNT(*) FILTER (WHERE orders >= 2))::numeric / NULLIF(COUNT(*), 0)
           AS repeat_purchase_rate
FROM customer_counts
