-- Review stock codes before labelling every entry as a merchandise product.
SELECT stock_code, SUM(sales_value_gbp) AS sales_value_gbp,
       SUM(quantity) AS units, COUNT(DISTINCT invoice_no) AS orders
FROM {{ ref('fct_sales_lines') }}
WHERE invoice_date >= DATE '2010-12-01' AND invoice_date < DATE '2011-12-01'
GROUP BY stock_code ORDER BY sales_value_gbp DESC
