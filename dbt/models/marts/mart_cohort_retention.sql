WITH customer_months AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month', order_date)::date AS month
    FROM {{ ref('int_customer_orders') }}
    WHERE order_date >= DATE '2010-12-01' AND order_date < DATE '2011-12-01'
), first_months AS (
    SELECT customer_id, MIN(month) AS cohort_month
    FROM customer_months GROUP BY customer_id
), sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM first_months GROUP BY cohort_month
), activity AS (
    SELECT f.cohort_month, m.month, COUNT(*) AS active_customers
    FROM customer_months m JOIN first_months f USING (customer_id)
    GROUP BY f.cohort_month, m.month
)
SELECT s.cohort_month, g.month::date AS activity_month,
       ((EXTRACT(YEAR FROM g.month) - EXTRACT(YEAR FROM s.cohort_month)) * 12
        + EXTRACT(MONTH FROM g.month) - EXTRACT(MONTH FROM s.cohort_month))::integer
           AS months_since_first_observed_purchase,
       s.cohort_size, COALESCE(a.active_customers, 0) AS active_customers,
       COALESCE(a.active_customers, 0)::numeric / s.cohort_size AS retention_rate
FROM sizes s
CROSS JOIN LATERAL GENERATE_SERIES(
    s.cohort_month::timestamp, TIMESTAMP '2011-11-01', INTERVAL '1 month'
) AS g(month)
LEFT JOIN activity a ON a.cohort_month = s.cohort_month AND a.month = g.month::date
ORDER BY 1, 3
