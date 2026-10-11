# Retail Revenue & Retention Analytics

An e-commerce analytics project exploring revenue performance, repeat purchasing and customer retention using the UCI Online Retail dataset.

**Status:** In progress. Initial dataset profiling is complete. Analytical models, SQL queries and dashboard development are planned.

## Business question

Which products, countries and customer groups contribute most to revenue, and how do repeat purchases shape business performance?

## Planned analysis

- Monthly sales value, cancellation value, order counts and average order value.
- Revenue contribution by product and country.
- Repeat purchase rate among identifiable customers.
- Monthly customer cohorts and retention.
- Revenue contribution from first-time observed and returning customers.

## Planned implementation

- Python and Pandas for data profiling and preparation.
- PostgreSQL and SQL for analytical queries.
- dbt for transformations, documentation and data quality tests.
- Power BI for an interactive business dashboard.

## Methodological considerations

Records without CustomerID will be excluded from customer-level analysis but assessed separately for sales reporting. Cancellation records, non-positive values and duplicate rows require explicit treatment.

Cohorts will use the first purchase observed in the dataset. December 2011 is incomplete and will be identified in time-based comparisons.

## Data source

Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository.  
https://doi.org/10.24432/C5BW33

Dataset license: CC BY 4.0.
