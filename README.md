# Retail Revenue & Retention Analytics

**An end-to-end e-commerce analytics case study | Python · PostgreSQL · SQL · dbt · Pandas · Matplotlib**

Analysis of sales performance, repeat purchasing, customer retention, customer segments, geographic concentration and product contributions using the historical [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online%2Bretail).

**Reporting period:** December 2010–November 2011 (12 complete months)
**Status:** Python/SQL analytics, native PostgreSQL dbt build, executive dashboard and business report completed. **Power BI authoring package prepared; interactive report not yet executed or validated.**

![Executive dashboard — retail revenue and retention analytics](assets/executive_dashboard.png)

> This dashboard is a **static Matplotlib image**, not a Power BI screenshot or a live interactive application. Figures represent eligible sales value under the documented data rules, not net accounting revenue or profit.

## Key results

| Metric | Result | Scope / definition |
| --- | ---: | --- |
| Eligible sales value | **£10,004,320.47** | Dec 2010–Nov 2011; cancellations reported separately |
| Orders | **19,141** | Distinct eligible sales invoices |
| Average order value | **£522.66** | Eligible sales value ÷ orders |
| Repeat purchase rate | **64.21%** | 2,759 of 4,297 identifiable customers; at least two observed orders |
| Weighted M1 retention | **18.91%** | Jan–Aug 2011 first-observed cohorts, 2,432 customers |
| Weighted M3 retention | **22.74%** | Same cohorts and observation horizon |
| UK share of sales value | **84.06%** | Share of eligible sales value across countries |
| November 2011 MoM growth | **+30.63%** | November compared with October 2011 |

## Business findings

1. **November sales rose primarily with order volume.** Eligible sales value reached **£1,503,866.78** in November 2011 (+30.63% month over month). Orders increased **35.74%**, while average order value fell **3.76%**.
2. **Repeat purchases were common, but should not be confused with monthly retention.** Among identifiable customers, **64.21%** placed at least two eligible orders in the observation window. Weighted activity in specific subsequent months was **18.91% at M1** and **22.74% at M3** for comparable Jan–Aug cohorts.
3. **Customer-ID completeness is a material analytical limitation.** Revenue from transactions without a CustomerID rose by **£232,039.89** from October to November, approximately **65.8% of the net change** in monthly sales value. This does not identify a causal driver of growth.
4. **Sales were highly concentrated geographically.** The **United Kingdom represented 84.06%** of eligible sales value. Ireland (EIRE), the Netherlands, Germany and France were the leading non-UK markets.
5. **Revenue and unit volume tell different product stories.** **Regency Cakestand 3 Tier (22423)** led the preliminary merchandise-candidate ranking at **£168,162.42**. The top 10 selected stock codes accounted for **8.52%** of eligible sales value **within the stock-code-format-filtered subset**, not the entire merchandise universe.

For methodology, detailed charts, recommendations and limitations, read the **[Business Insights Report](reports/business_insights.md)**.

## Visual analysis

| Analysis | Visualisation |
| --- | --- |
| Executive overview | [Executive analytics dashboard](assets/executive_dashboard.png) |
| Monthly performance | [Monthly revenue](assets/monthly_revenue_growth.png) |
| Cohort behaviour | [M1–M3 retention heatmap](assets/cohort_retention_heatmap.png) |
| Customer contributions | [Revenue composition by customer group](assets/customer_revenue_segmentation.png) |
| Geographic concentration | [Top 10 countries](assets/top_countries_revenue.png) |
| International markets | [Top 10 markets excluding UK](assets/top_international_markets.png) |
| Stock-code contribution | [Top 10 merchandise candidates](assets/top_products_revenue.png) |

### Monthly sales performance

![Monthly revenue performance](assets/monthly_revenue_growth.png)

### Customer retention

![Cohort retention heatmap](assets/cohort_retention_heatmap.png)

*Cohorts are defined by first **observed** eligible purchase, not verified customer acquisition. The heatmap shows purchasing activity during specific months, so M3 may exceed M1.*

## Data pipeline and architecture

```text
UCI Online Retail XLSX (541,909 source rows)
             |
             v
Python preparation & quality flags (src/prepare_data.py)
             |
             v
PostgreSQL source table (retail.invoice_lines)
             |
             v
dbt staging -> intermediate -> analytical marts
             |
             +--> SQL business metrics and validation
             +--> Python/Pandas visualisations and static dashboard
             +--> Business Insights Report
             +--> Power BI input tables and authoring package (not yet run in Power BI)
```

The prepared dataset preserves **541,909 source rows** and flags eligibility, cancellations, duplicates and missing identifiers. The primary analytical window omits incomplete December 2011. The eligible-sale flag applies to **524,878 prepared rows** across the source period; the dashboard totals cover the 12 complete reporting months.

### Components

- **[Python preparation](src/prepare_data.py)** and **[metric definitions](docs/metric_definitions.md)** — source preservation, eligibility rules and data-loading documentation.
- **[PostgreSQL schema](sql/01_schema.sql)** and **[analytical SQL](sql/02_analysis.sql)** — source storage and independent queries.
- **[dbt project](dbt/README.md)** — 10 analytical models (staging, facts, intermediate models, and marts) and 48 data-quality tests.
- **[Python analysis](src/analyse_data.py)** and **[visualisation pipeline](src/build_visuals.py)** — reconciled summaries, charts and duplicate sensitivity checks.
- **[Executive dashboard script](src/create_executive_dashboard.py)** — generates the static executive overview from locally exported analytics tables.
- **[Power BI authoring package](powerbi/README.md)** — CSV tables, Power Query scripts, DAX measure definitions, relationships, theme and design preview. **Not a completed Power BI report.**

## Validation and reproducibility

**Native PostgreSQL/dbt:** On **12 October 2026**, `dbt build` succeeded against **PostgreSQL 18.6 on Apple Silicon**, creating **10 view models** and passing **48 data tests** (`PASS=58 WARN=0 ERROR=0 SKIP=0`, including model builds). dbt documentation was generated successfully. See the [native build log](reports/dbt_native_build_2026-10-12.log).

**Independent checks:** The six standalone analytical SQL outputs were executed using **PGlite (PostgreSQL 18.3)** against the prepared dataset and compared with Python results. See [SQL validation](reports/sql_validation.json) and [dbt validation](reports/dbt_validation.json). These are separate from the subsequent successful native dbt build.

**Reproduce the base analysis:**

1. Download the source workbook from [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online%2Bretail).
2. Install Python dependencies for the analysis (`pandas`, `openpyxl`, `matplotlib`, `numpy`) and follow the detailed [source-table creation/loading instructions](docs/metric_definitions.md).
3. From the repository root, generate the prepared data and Python summaries:

```bash
python src/prepare_data.py "/path/to/Online Retail.xlsx"
python src/analyse_data.py data/processed/retail_lines.csv.gz
python src/build_visuals.py data/processed/retail_lines.csv.gz
```

4. For dbt, follow the [dbt setup guide](dbt/README.md), install `dbt/requirements.txt`, configure a **local** `profiles.yml` with credentials outside version control, and run:

```bash
dbt debug --project-dir dbt
dbt parse --project-dir dbt
dbt build --project-dir dbt
dbt docs generate --project-dir dbt
```

Dashboard and additional portfolio charts depend on the local CSV exports produced from the project's PostgreSQL marts; the raw workbook and local database are **not** committed to GitHub. See the relevant scripts in [`src/`](src/) for their expected local inputs.

## Power BI: prepared, not yet validated

The [`powerbi/`](powerbi/) directory contains six prepared CSV tables, Power Query `.pq` definitions, ten DAX measure definitions, relationship guidance, a theme and a Python-rendered design preview. **All eight Power Query files passed syntax checks, but Power Query and DAX have not yet been executed in Power BI, and no `.pbix`/`.pbip` report has been completed.** See [Power BI setup and acceptance checks](powerbi/README.md) and [validation status](powerbi/validation.json).

This status is deliberately separate from the **completed static Python dashboard** above.

## Methodological limitations

- **Eligible sales value is not profit or net revenue.** Cancellations are shown separately and are not linked back to original sale dates for netting.
- **Missing CustomerIDs** remain in eligible sales totals but are excluded from identifiable-customer metrics.
- **First observed purchase** is not necessarily first-ever purchase; the beginning and end of the historical window censor customer activity.
- **Cohort retention** measures activity in a particular observed month, not continuous use or causal loyalty effects.
- **Stock-code heuristics** can include or exclude non-merchandise records; merchandise-only recommendations require manual review.
- The **2010–2011 dataset** does not support claims about present-day market conditions or causal effectiveness of marketing initiatives.
- Exact duplicate sensitivity is documented in the original analysis; including flagged duplicates increases sales value by approximately **0.24%** under that comparison.

See [full findings and limitations](reports/findings.md) and the [Business Insights Report](reports/business_insights.md).

## Data source and attribution

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. Licensed **CC BY 4.0**. Figures, metrics and visualisations in this repository were derived under the project's documented analytical rules.
