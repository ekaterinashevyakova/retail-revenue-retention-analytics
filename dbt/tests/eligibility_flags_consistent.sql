select source_row
from {{ ref('stg_invoice_lines') }}
where is_cancellation is distinct from (upper(invoice_no) like 'C%')
   or has_customer_id is distinct from (customer_id is not null)
   or eligible_sale is distinct from
      (not is_duplicate and not is_cancellation and quantity > 0 and unit_price > 0)
   or eligible_cancellation is distinct from
      (not is_duplicate and is_cancellation and quantity < 0 and unit_price > 0)
