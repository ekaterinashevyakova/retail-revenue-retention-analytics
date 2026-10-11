# Retail sales and customer retention findings

## Scope and status

This analysis covers the twelve complete months from 1 December 2010 to 30 November 2011 using UCI Online Retail. Results were computed in Python from the prepared dataset. All six accompanying SQL queries were executed using PostgreSQL 18.3 via PGlite 0.5.8 (WebAssembly) and reconciled against Python outputs. Verification on a native PostgreSQL server remains pending. The dbt project is authored and parsed; model SQL and equivalent quality assertions passed direct PGlite checks. A full dbt build remains unverified. A Power BI authoring package is prepared, with reconciled input tables and syntax-checked Power Query definitions. Power BI execution and completed report verification remain pending.

## Results

| Metric | Result |
| --- | ---: |
| Eligible sales value | GBP 10,004,320.47 |
| Eligible cancellation value, reported separately | GBP 688,890.46 |
| Eligible sales orders | 19,141 |
| Average order value | GBP 522.66 |
| Identifiable purchasing customers | 4,297 |
| Customers with at least two orders in the window | 2,759 |
| Repeat purchase rate among identifiable customers | 64.21% |

Sales value is transaction value under the documented rules. It is not profit or audited accounting revenue. Cancellation value follows cancellation dates and is not matched back to original sale months.

## Interpretation

- The United Kingdom accounts for approximately 84.06% of eligible sales value. Country comparisons should distinguish the domestic market from smaller international markets.
- Repeat purchases are common among identifiable customers: 2,759 of 4,297 placed at least two eligible orders within the observation window. This describes observed behaviour and does not prove that a retention intervention worked.
- GBP 6,152,193.32 comes from customers whose first observed purchase month precedes the reporting month. GBP 2,217,825.13 comes from customers in their first observed purchase month. A further GBP 1,634,302.02 has no customer identifier and cannot be assigned to either group.
- Of the 885 customers first observed in December 2010, 324 purchased again in January 2011, giving month-one retention of 36.61%. This earliest cohort may contain existing customers whose earlier purchases fall outside the dataset.

These findings support prioritising further analysis of repeat purchasing and UK customer segments. The dataset does not establish why customers return or whether a particular campaign would improve retention.

## Validation and limitations

Sales totals reconcile exactly across monthly, country, stock-code and customer-group summaries using decimal arithmetic. Orders reconcile between monthly and overall summaries. Eligible sales invoices have one country in the analysed window. Cohort rates are between zero and one, and month-zero retention is 100%.

SQL validation loaded all 541,909 prepared source rows and compared 12 monthly rows, one repeat-purchase summary, 78 cohort rows, 35 customer-group rows, 38 country rows and 3,919 stock-code rows. Amounts, counts and units match exactly. Average order value uses a tolerance of 1e-16 GBP; retention and repeat purchase rates use 1e-15. See `reports/sql_validation.json` for the engine version and comparison results.

All source rows are retained in preparation. Exact duplicates after the first occurrence are flagged and excluded from analytical views as an assumption. Including these flagged duplicates increases sales value from GBP 10,004,320.47 to GBP 10,027,891.86, a difference of GBP 23,571.39 (0.24% of the base value). Average order value increases from GBP 522.66 to GBP 523.90. Order counts, identifiable customer counts and the repeat purchase rate are unchanged. Non-positive prices and negative quantities without a cancellation invoice prefix are retained for inspection and excluded from eligible sales and cancellation views.

Missing customer IDs are excluded from customer metrics but retained in sales reporting. Later cohorts have shorter follow-up. Unobserved future months are omitted, while observable months without repeat purchasing are recorded as zero. Incomplete December 2011 is excluded from these complete-month results. Some stock codes represent delivery or adjustment entries and require review before merchandise-level recommendations. Many customers are wholesalers, so the average order value should not be presented as a typical consumer basket.

The dbt project defines 10 models and 48 tests. `dbt parse` passed. Direct PGlite execution of model SQL and equivalent assertions returned no failing rows, and all six marts matched the reconciled Python outputs under the same comparison tolerances. This was not a successful `dbt build`: local socket restrictions prevented the dbt adapter from connecting. See `reports/dbt_validation.json` and `dbt/README.md`.

## Reproduction

Prepare the official source with `src/prepare_data.py`, then run:

```bash
python src/analyse_data.py data/processed/retail_lines.csv.gz
```

The script exports monthly metrics, cohort retention, customer-group sales, country sales, stock-code sales and a JSON summary into `reports/`. Definitions and preparation rules are documented in `docs/metric_definitions.md`. PostgreSQL queries are in `sql/02_analysis.sql`.

Generate figures and the duplicate sensitivity summary with:

```bash
python src/build_visuals.py data/processed/retail_lines.csv.gz
```

Source: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. CC BY 4.0.
