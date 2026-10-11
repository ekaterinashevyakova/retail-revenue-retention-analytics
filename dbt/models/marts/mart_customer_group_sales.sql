WITH first_months AS (
    SELECT customer_id, DATE_TRUNC('month', MIN(order_date))::date AS first_month
    FROM {{ ref('int_customer_orders') }} GROUP BY customer_id
)
SELECT DATE_TRUNC('month', s.invoice_date)::date AS month,
       CASE WHEN NOT s.has_customer_id THEN 'Unknown customer'
            WHEN f.first_month = DATE_TRUNC('month', s.invoice_date)::date
                THEN 'First observed purchase month'
            ELSE 'Returning customer' END AS customer_group,
       SUM(s.sales_value_gbp) AS sales_value_gbp
FROM {{ ref('fct_sales_lines') }} s LEFT JOIN first_months f USING (customer_id)
WHERE s.invoice_date >= DATE '2010-12-01' AND s.invoice_date < DATE '2011-12-01'
GROUP BY 1, 2 ORDER BY 1, 2
