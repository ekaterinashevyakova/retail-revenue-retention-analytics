WITH sales AS (
    SELECT DATE_TRUNC('month', invoice_date)::date AS month,
           SUM(sales_value_gbp) AS sales_value_gbp,
           COUNT(DISTINCT invoice_no) AS orders
    FROM {{ ref('fct_sales_lines') }}
    WHERE invoice_date >= DATE '2010-12-01'
      AND invoice_date < DATE '2011-12-01'
    GROUP BY 1
), cancellations AS (
    SELECT DATE_TRUNC('month', invoice_date)::date AS month,
           SUM(cancellation_value_gbp) AS cancellation_value_gbp
    FROM {{ ref('fct_cancellation_lines') }}
    WHERE invoice_date >= DATE '2010-12-01'
      AND invoice_date < DATE '2011-12-01'
    GROUP BY 1
)
SELECT COALESCE(s.month, c.month) AS month,
       COALESCE(s.sales_value_gbp, 0) AS sales_value_gbp,
       COALESCE(c.cancellation_value_gbp, 0) AS cancellation_value_gbp,
       COALESCE(s.orders, 0) AS orders,
       s.sales_value_gbp / NULLIF(s.orders, 0) AS average_order_value_gbp
FROM sales s FULL OUTER JOIN cancellations c ON s.month = c.month
ORDER BY 1
