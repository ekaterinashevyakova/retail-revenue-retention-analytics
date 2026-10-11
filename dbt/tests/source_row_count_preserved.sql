select 'source_count_differs' as failure
where (select count(*) from {{ ref('stg_invoice_lines') }}) <>
      (select count(*) from {{ source('retail','invoice_lines') }})
