-- across countries unless each invoice is verified to have one country.
SELECT country, SUM(sales_value_gbp) AS sales_value_gbp,
       COUNT(DISTINCT invoice_no) AS orders
FROM {{ ref('fct_sales_lines') }}
WHERE invoice_date >= DATE '2010-12-01' AND invoice_date < DATE '2011-12-01'
GROUP BY country ORDER BY sales_value_gbp DESC
