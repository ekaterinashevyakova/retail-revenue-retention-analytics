"""Compute reproducible complete-month metrics from prepared retail lines."""

import argparse
import json
from decimal import Decimal
from pathlib import Path

import pandas as pd


def analyse(data, output_dir):
    data = data.copy()
    data["invoice_date"] = pd.to_datetime(data["invoice_date"], errors="raise")
    data["month"] = data["invoice_date"].dt.to_period("M").dt.to_timestamp()
    data["line_value"] = [Decimal(str(p)) * int(q) for p, q in zip(data.unit_price, data.quantity)]
    window = data.invoice_date.ge("2010-12-01") & data.invoice_date.lt("2011-12-01")
    sales = data.loc[window & data.eligible_sale].copy()
    cancellations = data.loc[window & data.eligible_cancellation].copy()
    cancellations["cancellation_value"] = -cancellations.line_value
    monthly = sales.groupby("month").agg(
        sales_value_gbp=("line_value", "sum"), orders=("invoice_no", "nunique")
    )
    monthly["cancellation_value_gbp"] = cancellations.groupby("month").cancellation_value.sum().reindex(monthly.index, fill_value=Decimal(0))
    monthly["average_order_value_gbp"] = [value / Decimal(int(n)) for value, n in zip(monthly.sales_value_gbp, monthly.orders)]
    customers = sales.loc[sales.has_customer_id].copy()
    order_counts = customers.groupby("customer_id").invoice_no.nunique()
    repeat_customers = int(order_counts.ge(2).sum())
    customer_months = customers[["customer_id", "month"]].drop_duplicates()
    first_month = customer_months.groupby("customer_id").month.min()
    cohort_data = customer_months.join(first_month.rename("cohort_month"), on="customer_id")
    sizes = first_month.value_counts().sort_index()
    activity = cohort_data.groupby(["cohort_month", "month"]).size()
    cohort_rows = []
    for cohort, size in sizes.items():
        for month in pd.date_range(cohort, "2011-11-01", freq="MS"):
            active = int(activity.get((cohort, month), 0))
            cohort_rows.append({"cohort_month": cohort, "activity_month": month,
                                "months_since_first_observed_purchase": (month.year-cohort.year)*12+month.month-cohort.month,
                                "cohort_size": int(size), "active_customers": active,
                                "retention_rate": active / int(size)})
    cohorts = pd.DataFrame(cohort_rows)
    sales = sales.join(first_month.rename("first_month"), on="customer_id")
    sales["customer_group"] = "Unknown customer"
    sales.loc[sales.has_customer_id & sales.month.eq(sales.first_month), "customer_group"] = "First observed purchase month"
    sales.loc[sales.has_customer_id & sales.month.gt(sales.first_month), "customer_group"] = "Returning customer"
    groups = sales.groupby(["month", "customer_group"]).line_value.sum().rename("sales_value_gbp")
    countries = sales.groupby("country").agg(sales_value_gbp=("line_value", "sum"), orders=("invoice_no", "nunique")).sort_values("sales_value_gbp", ascending=False)
    stocks = sales.groupby("stock_code").agg(sales_value_gbp=("line_value", "sum"), units=("quantity", "sum"), orders=("invoice_no", "nunique")).sort_values("sales_value_gbp", ascending=False)
    total = sum(sales.line_value, Decimal(0))
    assert monthly.sales_value_gbp.sum() == total == countries.sales_value_gbp.sum() == stocks.sales_value_gbp.sum() == groups.sum()
    assert monthly.orders.sum() == sales.invoice_no.nunique(), "Invoice spans multiple reporting months"
    assert sales.groupby("invoice_no").country.nunique().max() == 1, "Invoice spans multiple countries"
    assert cohorts.retention_rate.between(0, 1).all()
    assert cohorts.loc[cohorts.months_since_first_observed_purchase.eq(0), "retention_rate"].eq(1).all()
    summary = {
        "window": "2010-12-01 inclusive to 2011-12-01 exclusive",
        "sales_value_gbp": str(total),
        "cancellation_value_gbp": str(sum(cancellations.cancellation_value, Decimal(0))),
        "orders": int(sales.invoice_no.nunique()),
        "average_order_value_gbp": str(total / Decimal(int(sales.invoice_no.nunique()))),
        "identifiable_customers": len(order_counts),
        "repeat_customers": repeat_customers,
        "repeat_purchase_rate": repeat_customers / len(order_counts),
        "validation": "Python calculations reconciled. PostgreSQL execution not verified.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(output_dir / "monthly_metrics.csv")
    cohorts.to_csv(output_dir / "cohort_retention.csv", index=False)
    groups.to_csv(output_dir / "customer_group_sales.csv")
    countries.to_csv(output_dir / "country_sales.csv")
    stocks.to_csv(output_dir / "stock_code_sales.csv")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    data = pd.read_csv(args.input, dtype={"invoice_no": "string", "stock_code": "string", "customer_id": "string"})
    print(json.dumps(analyse(data, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
