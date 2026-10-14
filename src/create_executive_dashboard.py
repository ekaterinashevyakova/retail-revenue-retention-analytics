from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
OUTPUT = ROOT / "assets/executive_dashboard.png"

# Load validated analytical outputs
monthly = pd.read_csv(DATA / "monthly_metrics.csv")
groups = pd.read_csv(DATA / "customer_group_sales.csv")
countries = pd.read_csv(DATA / "country_revenue.csv")
cohorts = pd.read_csv(DATA / "cohort_retention_dashboard.csv")
repeat = pd.read_csv(DATA / "repeat_purchase_summary.csv")

monthly = monthly.sort_values("month")

# Calculate KPIs
total_revenue = monthly["revenue_gbp"].sum()
total_orders = int(monthly["orders"].sum())
overall_aov = total_revenue / total_orders

repeat_rate = float(
    repeat["repeat_purchase_rate"].iloc[0] * 100
)

uk_revenue = countries.loc[
    countries["country"] == "United Kingdom",
    "revenue_gbp"
].sum()

uk_share = 100 * uk_revenue / countries["revenue_gbp"].sum()

november_growth = (
    monthly["revenue_gbp"].iloc[-1]
    / monthly["revenue_gbp"].iloc[-2]
    - 1
) * 100

# Calculate weighted cohort retention
retention = cohorts.groupby("month_num").agg(
    active=("active_customers", "sum"),
    customers=("cohort_size", "sum")
)

retention["rate"] = (
    retention["active"] / retention["customers"] * 100
)

m1 = retention.loc[1, "rate"]
m3 = retention.loc[3, "rate"]

# Validate monthly reconciliation
group_totals = groups.groupby("month")["revenue_gbp"].sum()

monthly_totals = monthly.set_index("month")["revenue_gbp"]

difference = (
    monthly_totals - group_totals.reindex(monthly_totals.index)
).abs()

if difference.isna().any() or (difference > 0.05).any():
    raise SystemExit(
        "Monthly customer-group revenue does not reconcile."
    )

# Create dashboard
fig = plt.figure(figsize=(17, 12))

fig.suptitle(
    "RETAIL REVENUE & RETENTION ANALYTICS",
    fontsize=21,
    fontweight="bold",
    y=0.97
)

fig.text(
    0.5,
    0.925,
    "Executive Analytics Dashboard | December 2010 – November 2011",
    ha="center",
    fontsize=12
)

# KPI cards
kpis = [
    ("TOTAL SALES VALUE", f"£{total_revenue/1e6:.2f}M"),
    ("TOTAL ORDERS", f"{total_orders:,}"),
    ("AVERAGE ORDER VALUE", f"£{overall_aov:,.2f}"),
    ("REPEAT PURCHASE RATE", f"{repeat_rate:.2f}%"),
    ("UK REVENUE SHARE", f"{uk_share:.2f}%")
]

positions = [0.11, 0.30, 0.49, 0.68, 0.87]

for x, (label, value) in zip(positions, kpis):
    fig.text(
        x, 0.865, label,
        ha="center",
        fontsize=9
    )

    fig.text(
        x, 0.829, value,
        ha="center",
        fontsize=19,
        fontweight="bold"
    )

# Create four panels
axes = fig.subplots(2, 2)

plt.subplots_adjust(
    left=0.09,
    right=0.94,
    top=0.75,
    bottom=0.12,
    hspace=0.58,
    wspace=0.32
)

# Panel 1: Monthly Revenue
ax = axes[0, 0]

revenue_m = monthly["revenue_gbp"] / 1_000_000

ax.plot(
    monthly["month"],
    revenue_m,
    marker="o",
    linewidth=2
)

ax.set_title("Monthly Revenue", fontsize=13)
ax.set_ylabel("Sales Value (£M)")
ax.tick_params(axis="x", rotation=45, labelsize=8)
ax.grid(axis="y", alpha=0.2)

ax.annotate(
    f"Nov: +{november_growth:.2f}% MoM",
    xy=(len(monthly) - 1, revenue_m.iloc[-1]),
    xytext=(-110, -35),
    textcoords="offset points",
    arrowprops={"arrowstyle": "->"},
    fontsize=9
)

# Panel 2: Customer Revenue Composition
ax = axes[0, 1]

revenue_matrix = groups.pivot_table(
    index="month",
    columns="customer_group",
    values="revenue_gbp",
    aggfunc="sum",
    fill_value=0
).sort_index()

group_names = [
    "First observed purchase month",
    "Returning customer",
    "Unknown customer"
]

shares = revenue_matrix.reindex(
    columns=group_names,
    fill_value=0
)

shares = shares.div(shares.sum(axis=1), axis=0) * 100

bottom = pd.Series(0.0, index=shares.index)

for group in group_names:
    ax.bar(
        shares.index,
        shares[group],
        bottom=bottom,
        label=group
    )
    bottom += shares[group]

ax.set_title("Revenue by Customer Group", fontsize=13)
ax.set_ylabel("Share of Revenue (%)")
ax.set_ylim(0, 100)
ax.tick_params(axis="x", rotation=45, labelsize=8)
fig.legend(
    *ax.get_legend_handles_labels(),
    loc="lower center",
    bbox_to_anchor=(0.5, 0.08),
    ncol=3,
    frameon=False,
    fontsize=9
)

# Panel 3: Cohort Retention
ax = axes[1, 0]

matrix = cohorts.pivot(
    index="cohort",
    columns="month_num",
    values="retention_pct"
).sort_index()

heat = ax.imshow(
    matrix.values,
    cmap="Blues",
    aspect="auto",
    vmin=0,
    vmax=40
)

ax.set_xticks(range(len(matrix.columns)))
ax.set_xticklabels([f"M{x}" for x in matrix.columns])

ax.set_yticks(range(len(matrix.index)))
ax.set_yticklabels(matrix.index)

ax.set_title(
    f"Cohort Retention | M1: {m1:.1f}% · M3: {m3:.1f}%",
    fontsize=12
)

for i in range(len(matrix.index)):
    for j in range(len(matrix.columns)):
        value = matrix.iloc[i, j]

        ax.text(
            j, i,
            f"{value:.1f}%",
            ha="center",
            va="center",
            fontsize=8,
            color="white" if value >= 22 else "black"
        )

fig.colorbar(heat, ax=ax, shrink=0.8)

# Panel 4: International Markets
ax = axes[1, 1]

international = countries[
    countries["country"] != "United Kingdom"
].nlargest(6, "revenue_gbp").copy()

international["country"] = international["country"].replace(
    {"EIRE": "Ireland"}
)

international = international.sort_values("revenue_gbp")

bars = ax.barh(
    international["country"],
    international["revenue_gbp"] / 1000
)

ax.bar_label(
    bars,
    fmt="%.0f",
    padding=4,
    fontsize=8
)

ax.set_title(
    "Top International Markets (Excluding UK)",
    fontsize=12
)

ax.set_xlabel("Sales Value (£ thousands)")
ax.set_xlim(
    0,
    international["revenue_gbp"].max() / 1000 * 1.25
)

# Notes
fig.text(
    0.5,
    0.045,
    "Source: UCI Online Retail | Sales exclude cancellations; "
    "customer metrics require identifiable customers.\n"
    "Retention: January–August 2011 first-observed cohorts. "
    "Historical observational data; results are not causal.",
    ha="center",
    fontsize=9
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

fig.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("Executive Dashboard created successfully!")
print(f"Saved to: {OUTPUT}")
print(f"Total Sales Value: £{total_revenue:,.2f}")
print(f"Total Orders: {total_orders:,}")
print(f"Average Order Value: £{overall_aov:,.2f}")
print(f"Repeat Purchase Rate: {repeat_rate:.2f}%")
print(f"UK Revenue Share: {uk_share:.2f}%")
print(f"M1 Retention: {m1:.2f}%")
print(f"M3 Retention: {m3:.2f}%")
print(f"November Growth: {november_growth:.2f}%")
