select *, -quantity * unit_price as cancellation_value_gbp
from {{ ref('stg_invoice_lines') }}
where eligible_cancellation
