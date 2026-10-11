# Retail Revenue & Retention Analytics

An e-commerce analytics project examining sales performance, repeat purchasing and customer retention using UCI Online Retail.

**Status:** In progress. Python data preparation, complete-month analysis, visualisations and duplicate sensitivity checks are implemented. PostgreSQL queries are written but have not yet been executed in PostgreSQL. dbt and Power BI development remain planned.

## Business question

Which products, countries and customer groups contribute most to sales value, and how do repeat purchases shape business performance?

## Key results

For the twelve complete months from December 2010 to November 2011:

- GBP 10,004,320.47 in eligible sales value across 19,141 orders.
- Average order value of GBP 522.66.
- 64.21% repeat purchase rate among 4,297 identifiable customers.
- Including flagged duplicates increases sales value by approximately 0.24%. Order counts and the repeat purchase rate remain unchanged.

Sales value is transaction value under the documented preparation rules. It is not profit or audited accounting revenue. Many customers are wholesalers.

## Visual analysis

### Monthly sales and average order value

![Monthly sales and average order value](assets/monthly-sales-and-aov.png)

### Customer cohort retention

![Customer cohort retention](assets/cohort-retention.png)

Cohorts use the first purchase observed in the dataset. Blank cells indicate months outside the observation window, rather than zero retention.

### Sales by customer group

![Monthly sales by customer group](assets/customer-group-sales.png)

Customers are classified by their first observed purchase month. Sales without CustomerID remain a separate group.

## Implementation

- [Data preparation](src/prepare_data.py): preserves source rows, flags duplicates and cancellations, and exports a compressed CSV and quality report.
- [Python analysis](src/analyse_data.py): calculates monthly sales, cancellations, orders, average order value, repeat purchasing, cohort retention, country and stock-code contribution.
- [Visualisations and sensitivity checks](src/build_visuals.py): generates the figures and compares results with and without flagged duplicates.
- [PostgreSQL schema](sql/01_schema.sql) and [six analytical queries](sql/02_analysis.sql).
- [Metric definitions and loading instructions](docs/metric_definitions.md).
- [Findings and limitations](reports/findings.md).

Python sales totals reconcile across monthly, country, stock-code and customer-group summaries. Cohort rates and reporting-period boundaries were checked. These checks do not establish PostgreSQL execution.

## Reproduce the Python analysis

Download the official source from [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online%2Bretail) and extract the workbook locally. Install pandas, openpyxl, matplotlib and numpy in your Python environment, then run from the repository root:

```bash
python src/prepare_data.py "/path/to/Online Retail.xlsx"
python src/analyse_data.py data/processed/retail_lines.csv.gz
python src/build_visuals.py data/processed/retail_lines.csv.gz
```

Generated tables and summaries are written to `reports/`; figures are written to `assets/`. The raw dataset is not included in this repository.

## Methodological considerations

Missing CustomerID records are excluded from customer-level metrics but retained in sales reporting. Cancellations are reported separately by cancellation date. Exact duplicates after the first occurrence are excluded from the base case, with an inclusion sensitivity comparison.

Non-positive prices and negative quantities without a cancellation prefix are retained for inspection and excluded from eligible sales and cancellation views. December 2011 is incomplete and excluded from complete-month comparisons. First observed purchase is not necessarily actual customer acquisition. Delivery and adjustment stock codes require review before merchandise-level recommendations.

## Next development steps

- Execute the schema, data loading and analytical queries in PostgreSQL and reconcile results against Python outputs.
- Develop dbt transformations, documentation and data quality tests.
- Build a Power BI dashboard.
- Investigate customer segments and review merchandise versus non-merchandise stock codes.

## Data source

Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33.

Dataset license: CC BY 4.0. Figures and summaries are derived from this dataset using the documented analytical rules.
