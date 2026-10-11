select count(*) as month_count
from {{ ref('mart_monthly_metrics') }}
having count(*) <> 12
   or min(month) <> date '2010-12-01'
   or max(month) <> date '2011-11-01'
