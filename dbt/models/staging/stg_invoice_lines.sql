select source_row, invoice_no, stock_code, description, quantity,
       invoice_date, unit_price, customer_id, country,
       is_duplicate, is_cancellation, has_customer_id,
       eligible_sale, eligible_cancellation
from {{ source('retail', 'invoice_lines') }}
