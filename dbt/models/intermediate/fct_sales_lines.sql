select *, quantity * unit_price as sales_value_gbp
from {{ ref('stg_invoice_lines') }}
where eligible_sale
