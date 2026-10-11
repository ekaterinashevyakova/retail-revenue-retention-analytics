-- PostgreSQL queries. Run after 01_schema.sql and loading prepared data.
-- Complete-month reporting window: 2010-12-01 <= date < 2011-12-01.
-- Sales and cancellations use the separately documented eligibility rules.

-- 1. Monthly sales, cancellations and average order value (GBP).
WITH sales AS (
    SELECT DATE_TRUNC('month', invoice_date)::date AS month,
           SUM(sales_value_gbp) AS sales_value_gbp,
           COUNT(DISTINCT invoice_no) AS orders
    FROM retail.sales_lines
    WHERE invoice_date >= DATE '2010-12-01'
      AND invoice_date < DATE '2011-12-01'
    GROUP BY 1
), cancellations AS (
    SELECT DATE_TRUNC('month', invoice_date)::date AS month,
           SUM(cancellation_value_gbp) AS cancellation_value_gbp
    FROM retail.cancellation_lines
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
ORDER BY 1;

-- 2. Repeat purchase rate among identifiable customers in the same window.
WITH customer_counts AS (
    SELECT customer_id, COUNT(DISTINCT invoice_no) AS orders
    FROM retail.customer_orders
    WHERE order_date >= DATE '2010-12-01' AND order_date < DATE '2011-12-01'
    GROUP BY customer_id
)
SELECT COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE orders >= 2) AS repeat_customers,
       (COUNT(*) FILTER (WHERE orders >= 2))::numeric / NULLIF(COUNT(*), 0)
           AS repeat_purchase_rate
FROM customer_counts;

-- 3. Monthly cohorts. Output only observable complete months, including zeroes.
WITH customer_months AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month', order_date)::date AS month
    FROM retail.customer_orders
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
ORDER BY 1, 3;

-- 4. First-time observed versus returning customer sales, customer-month basis.
WITH first_months AS (
    SELECT customer_id, DATE_TRUNC('month', MIN(order_date))::date AS first_month
    FROM retail.customer_orders GROUP BY customer_id
)
SELECT DATE_TRUNC('month', s.invoice_date)::date AS month,
       CASE WHEN NOT s.has_customer_id THEN 'Unknown customer'
            WHEN f.first_month = DATE_TRUNC('month', s.invoice_date)::date
                THEN 'First observed purchase month'
            ELSE 'Returning customer' END AS customer_group,
       SUM(s.sales_value_gbp) AS sales_value_gbp
FROM retail.sales_lines s LEFT JOIN first_months f USING (customer_id)
WHERE s.invoice_date >= DATE '2010-12-01' AND s.invoice_date < DATE '2011-12-01'
GROUP BY 1, 2 ORDER BY 1, 2;

-- 5. Country contribution. Invoice counts by country must not be summed
-- across countries unless each invoice is verified to have one country.
SELECT country, SUM(sales_value_gbp) AS sales_value_gbp,
       COUNT(DISTINCT invoice_no) AS orders
FROM retail.sales_lines
WHERE invoice_date >= DATE '2010-12-01' AND invoice_date < DATE '2011-12-01'
GROUP BY country ORDER BY sales_value_gbp DESC;

-- 6. Stock code contribution. Source includes delivery/adjustment codes.
-- Review stock codes before labelling every entry as a merchandise product.
SELECT stock_code, SUM(sales_value_gbp) AS sales_value_gbp,
       SUM(quantity) AS units, COUNT(DISTINCT invoice_no) AS orders
FROM retail.sales_lines
WHERE invoice_date >= DATE '2010-12-01' AND invoice_date < DATE '2011-12-01'
GROUP BY stock_code ORDER BY sales_value_gbp DESC;
