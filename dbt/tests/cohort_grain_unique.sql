select cohort_month, activity_month, count(*)
from {{ ref('mart_cohort_retention') }}
group by 1, 2 having count(*) > 1
