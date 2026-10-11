# Retail analytics dbt project

## Status

Ten models and 48 data tests are defined. `dbt parse` passed with dbt Core 1.12.5 and dbt-postgres 1.11.0. Model SQL and SQL equivalents of the defined assertions were executed directly in PostgreSQL 18.3 via PGlite 0.5.8, using all 541,909 prepared rows. This is not a verified `dbt build`: the validation environment prohibits binding local sockets. A full build on a native PostgreSQL server remains pending.

## Model grains

| Model | Grain / purpose |
| --- | --- |
| stg_invoice_lines | One prepared source row, preserving all flags and the full source period |
| fct_sales_lines | One eligible sales line, including sales without CustomerID |
| fct_cancellation_lines | One eligible cancellation line, with absolute value by cancellation date |
| int_customer_orders | One invoice / known-customer combination |
| mart_monthly_metrics | One complete calendar month, December 2010–November 2011 |
| mart_repeat_purchase | One summary row for identifiable customers in the complete-month window |
| mart_cohort_retention | One first-observed-purchase cohort / observable activity month |
| mart_customer_group_sales | One complete month / customer group |
| mart_country_sales | One country in the complete-month window |
| mart_stock_code_sales | One stock code in the complete-month window |

The staging model reads `retail.invoice_lines`. The sales and cancellation models apply the prepared eligibility flags. Customer orders aggregate eligible known-customer sales. Marts depend on these intermediate models and preserve the metric definitions used in the independently validated SQL queries.

## Data quality checks

The project defines 35 generic tests (`unique` and `not_null`) and 13 singular SQL tests. These check composite grains, eligibility flags, the complete-month window, customer-group labels, retention bounds, repeat purchase consistency, average order value, invoice-country consistency, order reconciliation, sales reconciliation and preservation of source row counts.

Source freshness is not configured because this is a fixed historical dataset. Tests assess the prepared dataset and modelling assumptions; they do not establish causal effects, profit or audited revenue.

## Run on your PostgreSQL database

1. Prepare the official UCI workbook using `src/prepare_data.py` from the repository root.
2. Create the source table with `sql/01_schema.sql` and load the compressed CSV following `docs/metric_definitions.md`. Load the source only once.
3. Install the tested dbt versions from the repository root:

```bash
python -m pip install -r dbt/requirements.txt
```

4. Copy `dbt/profiles.example.yml` into your local dbt profiles directory as `profiles.yml`. Set `DBT_HOST`, `DBT_PORT`, `DBT_USER`, `DBT_DATABASE`, `DBT_SCHEMA` and `DBT_ENV_SECRET_PASSWORD` in your own environment. Use a dedicated writable target schema; keep the source schema `retail` separate. Connection credentials must stay outside version control.
5. Run from the repository root:

```bash
dbt debug --project-dir dbt
dbt parse --project-dir dbt
dbt build --project-dir dbt
dbt docs generate --project-dir dbt
dbt docs serve --project-dir dbt
```

If you use a non-default profiles directory, add `--profiles-dir /path/to/local/profiles` to each command. The example uses one thread for predictable local development. `target/`, `logs/`, `dbt_packages/` and local credentials are excluded from version control.

## Interpretation limits

First observed purchase is not actual acquisition. Observable inactive cohort months are zero; future months are omitted. Missing customer IDs remain in sales totals and are excluded from customer metrics. Cancellations are reported separately and are not attributed back to original sales. Stock codes may include delivery and adjustments. The first-observed / returning distinction is at customer-month level, so another order in the first observed month stays in the first-observed group.

## Evidence

See `reports/dbt_validation.json` in the repository root for parse status, directly executed model SQL, assertion results, engine versions and the outstanding full-build limitation. SQL validation uses exact comparisons for amounts and counts; rates and average order values use explicitly recorded tolerances.
