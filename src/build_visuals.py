"""Build portfolio figures and assess sensitivity to duplicate exclusion."""

import argparse
import json
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd


def sensitivity(data):
    dates = pd.to_datetime(data.invoice_date)
    window = dates.ge("2010-12-01") & dates.lt("2011-12-01")
    sale_rule = window & ~data.is_cancellation & data.quantity.gt(0) & data.unit_price.gt(0)
    results = {}
    for name, keep in [("exclude_flagged_duplicates", ~data.is_duplicate),
                       ("include_flagged_duplicates", pd.Series(True, index=data.index))]:
        sales = data.loc[sale_rule & keep]
        value = sum((Decimal(str(p)) * int(q) for p, q in zip(sales.unit_price, sales.quantity)), Decimal(0))
        orders = int(sales.invoice_no.nunique())
        counts = sales.loc[sales.has_customer_id].groupby("customer_id").invoice_no.nunique()
        repeats = int(counts.ge(2).sum())
        results[name] = {"sales_value_gbp": str(value), "orders": orders,
                         "average_order_value_gbp": str(value / Decimal(orders)),
                         "identifiable_customers": len(counts), "repeat_customers": repeats,
                         "repeat_purchase_rate": repeats / len(counts)}
    base = Decimal(results["exclude_flagged_duplicates"]["sales_value_gbp"])
    added = Decimal(results["include_flagged_duplicates"]["sales_value_gbp"]) - base
    results["sales_difference_gbp"] = str(added)
    results["sales_difference_percent_of_base"] = str(added / base * 100)
    return results


def build(reports, assets):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": "#334155", "text.color": "#17263c",
                         "axes.edgecolor": "#cbd5e1", "xtick.color": "#475569",
                         "ytick.color": "#475569", "savefig.facecolor": "white"})
    navy, teal, gray = "#245786", "#238c88", "#c4cbd4"
    assets.mkdir(parents=True, exist_ok=True)
    monthly = pd.read_csv(reports / "monthly_metrics.csv")
    labels = pd.to_datetime(monthly.month).dt.strftime("%b\n%Y")
    x = np.arange(len(monthly))
    fig, axes = plt.subplots(2, 1, figsize=(11.8, 7.6), sharex=True)
    fig.subplots_adjust(top=.85, bottom=.13, left=.10, right=.96, hspace=.30)
    fig.suptitle("Monthly sales and average order value", x=.10, ha="left", fontsize=20, weight="bold")
    fig.text(.10, .91, "Complete months: December 2010–November 2011", fontsize=12, color="#64748b")
    axes[0].plot(x, monthly.sales_value_gbp, color=navy, marker="o", lw=2.4)
    axes[0].set_ylabel("Sales value (GBP)")
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v / 1e6:.1f}m"))
    axes[1].plot(x, monthly.average_order_value_gbp, color=teal, marker="o", lw=2.4)
    axes[1].set_ylabel("Average order value (GBP)")
    axes[1].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v:,.0f}"))
    for ax in axes:
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", color="#e2e8f0", lw=.8)
        ax.set_axisbelow(True)
    axes[1].set_xticks(x, labels)
    fig.text(.10, .035, "UCI Online Retail · Flagged duplicates excluded · Sales value is transaction value; cancellations reported separately.", fontsize=9, color="#64748b")
    fig.savefig(assets / "monthly-sales-and-aov.png", dpi=180)
    plt.close(fig)

    cohorts = pd.read_csv(reports / "cohort_retention.csv")
    matrix = cohorts.pivot(index="cohort_month", columns="months_since_first_observed_purchase", values="retention_rate").sort_index()
    sizes = cohorts.groupby("cohort_month").cohort_size.first().reindex(matrix.index)
    fig, ax = plt.subplots(figsize=(12.2, 8.1))
    fig.subplots_adjust(left=.19, right=.89, top=.84, bottom=.16)
    fig.suptitle("Customer cohort retention", x=.07, ha="left", fontsize=21, weight="bold")
    fig.text(.07, .91, "Share of each cohort purchasing in each observed month", fontsize=12, color="#64748b")
    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad("#f4f6f9")
    values = matrix.to_numpy() * 100
    im = ax.imshow(np.ma.masked_invalid(values), cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(matrix.columns)), [str(n) for n in matrix.columns])
    ax.set_xlabel("Months since first observed purchase", labelpad=12)
    ax.set_yticks(range(len(matrix)), [pd.Timestamp(m).strftime("%b %Y") + f"  (n={int(sizes.loc[m])})" for m in matrix.index])
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            if np.isfinite(values[i, j]):
                ax.text(j, i, f"{values[i, j]:.0f}%", ha="center", va="center", fontsize=10, color="white" if values[i, j] >= 55 else "#17263c")
    ax.set_xticks(np.arange(-.5, len(matrix.columns), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(matrix), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="both", length=0)
    cb = fig.colorbar(im, ax=ax, fraction=.04, pad=.035)
    cb.set_label("Retention (%)")
    fig.text(.07, .07, "Blank cells: future months outside the complete-month observation window. Month 0 is 100% by definition.", fontsize=10, color="#64748b")
    fig.text(.07, .035, "UCI Online Retail · Identifiable customers only · First observed purchase may differ from actual acquisition.", fontsize=9, color="#64748b")
    fig.savefig(assets / "cohort-retention.png", dpi=180)
    plt.close(fig)

    groups = pd.read_csv(reports / "customer_group_sales.csv")
    table = groups.pivot(index="month", columns="customer_group", values="sales_value_gbp").fillna(0).sort_index()
    order = ["First observed purchase month", "Returning customer", "Unknown customer"]
    table = table.reindex(columns=order, fill_value=0)
    assert np.allclose(table.sum(axis=1).values, monthly.sales_value_gbp.values)
    fig, ax = plt.subplots(figsize=(12.2, 7.1))
    fig.subplots_adjust(left=.09, right=.97, top=.77, bottom=.18)
    fig.suptitle("Monthly sales by customer group", x=.09, ha="left", fontsize=21, weight="bold")
    fig.text(.09, .91, "Customer classification uses the first observed purchase month", fontsize=12, color="#64748b")
    bottom = np.zeros(len(table))
    for group, color in zip(order, [navy, teal, gray]):
        ax.bar(np.arange(len(table)), table[group], bottom=bottom, label=group, color=color, width=.67)
        bottom += table[group].to_numpy()
    ax.set_xticks(np.arange(len(table)), pd.to_datetime(table.index).strftime("%b\n%Y"))
    ax.set_ylabel("Sales value (GBP)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v/1e6:.1f}m"))
    ax.grid(axis="y", color="#e2e8f0", lw=.8)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=3, frameon=False, fontsize=10)
    fig.text(.09, .055, "Unknown customer: missing CustomerID. First-month purchases are grouped together, including repeat orders that month.", fontsize=10, color="#64748b")
    fig.text(.09, .025, "UCI Online Retail · December 2010–November 2011 · Flagged duplicates excluded.", fontsize=9, color="#64748b")
    fig.savefig(assets / "customer-group-sales.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Prepared retail_lines.csv.gz")
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--assets-dir", type=Path, default=Path("assets"))
    args = parser.parse_args()
    data = pd.read_csv(args.input, dtype={"invoice_no": "string", "stock_code": "string", "customer_id": "string"})
    result = sensitivity(data)
    base = json.loads((args.reports_dir / "summary.json").read_text())
    assert Decimal(result["exclude_flagged_duplicates"]["sales_value_gbp"]) == Decimal(base["sales_value_gbp"])
    (args.reports_dir / "duplicate_sensitivity.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    build(args.reports_dir, args.assets_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
