select * from {{ ref('mart_cohort_retention') }}
where retention_rate < 0 or retention_rate > 1 or cohort_size <= 0
   or active_customers < 0 or active_customers > cohort_size
   or (months_since_first_observed_purchase = 0 and retention_rate <> 1)
   or activity_month < cohort_month or activity_month >= date '2011-12-01'
   or cohort_month < date '2010-12-01'
   or months_since_first_observed_purchase < 0
