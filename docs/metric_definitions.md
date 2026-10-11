# Data preparation and metric definitions

Source: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. CC BY 4.0.

The source covers 1 December 2010 to 9 December 2011. One row represents an invoice line, not a complete order. Prices are in GBP. The retailer also serves wholesale customers.

## Preparation rules

- Preserve every source row and its original worksheet row number.
- Flag exact duplicate rows after the first occurrence. Exclude these flagged rows from analytical views as an explicit assumption. Identical lines could represent genuine repeated entries, so results should be checked for sensitivity to this rule.
- Eligible sales require a non-cancelled invoice, positive quantity and positive price.
- Eligible cancellations require an invoice beginning with C, negative quantity and positive price. Report their absolute value separately. Cancellation dates are not assumed to match the original sale dates.
- Keep other records for inspection, including non-positive prices and negative quantities on invoices without C.
- Retain sales without CustomerID for overall sales reporting. Exclude them from customer-level metrics.
- Preserve source timestamps. No source timezone is established.

## Planned metrics

| Metric | Definition |
| --- | --- |
| Sales value | Sum of Quantity × UnitPrice for eligible sales, in GBP. This is transaction value, not profit or audited accounting revenue. |
| Cancellation value | Sum of −Quantity × UnitPrice for eligible cancellations, in GBP. |
| Orders | Count of distinct eligible sales invoices. |
| Average order value | Eligible sales value divided by eligible sales orders for the same population and period. |
| Repeat purchase rate | Identifiable customers with at least two distinct eligible sales invoices divided by identifiable customers with at least one, within a stated observation window. |
| Cohort retention | Customers with an eligible purchase in a given month since their first observed purchase month, divided by the original cohort size. Month zero is 100%. |
| Returning customer sales | Sales from customers whose first observed purchase month precedes the reporting month. This classification applies at the customer-month level. |

## Comparability

The first observed purchase is not necessarily the customer's first-ever purchase. Later cohorts have shorter follow-up. Unobserved future months must remain unavailable rather than being recorded as zero retention. December 2011 is incomplete and should be labelled or excluded when comparing complete months. The data does not support claims about profit, marketing attribution or causal retention improvements.

## Local run

Install pandas and openpyxl in your Python environment. From the repository root:

```bash
python src/prepare_data.py "/path/to/Online Retail.xlsx"
```

The script writes the compressed CSV `data/processed/retail_lines.csv.gz` and `quality_report.json`. Run `sql/01_schema.sql` in PostgreSQL. On macOS or Linux with gzip installed, use psql's local `\copy` command to decompress and load the CSV:

```sql
\copy retail.invoice_lines FROM PROGRAM 'gzip -dc data/processed/retail_lines.csv.gz' WITH (FORMAT csv, HEADER true);
```

Alternatively, decompress the gzip archive locally and load that CSV with `\copy ... FROM 'path/to/retail_lines.csv'`. The CSV column order matches the table. Avoid loading the same source twice. The worksheet row primary key detects repeated loads. SQL execution and database loading must be verified in a PostgreSQL environment.
