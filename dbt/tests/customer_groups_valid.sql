select * from {{ ref('mart_customer_group_sales') }}
where customer_group not in ('Unknown customer','First observed purchase month','Returning customer')
   or month < date '2010-12-01' or month >= date '2011-12-01'
   or sales_value_gbp <= 0
