from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

# Load customer revenue data
df = pd.read_csv(
    ROOT / "data/processed/customer_group_sales.csv"
)

# Create monthly revenue matrix
revenue = df.pivot_table(
    index="month",
    columns="customer_group",
    values="revenue_gbp",
    aggfunc="sum",
    fill_value=0
).sort_index()

# Define customer groups
groups = [
    "First observed purchase month",
    "Returning customer",
    "Unknown customer"
]

revenue = revenue.reindex(
    columns=groups,
    fill_value=0
)

# Calculate percentage of monthly revenue
shares = revenue.div(
    revenue.sum(axis=1),
    axis=0
) * 100

# Create chart
fig, ax = plt.subplots(figsize=(13, 6))

bottom = pd.Series(
    0.0,
    index=shares.index
)

for group in groups:
    ax.bar(
        shares.index,
        shares[group],
        bottom=bottom,
        label=group,
        width=0.8
    )

    bottom += shares[group]

ax.set_title(
    "Revenue Composition by Customer Group\n"
    "UCI Online Retail | Dec 2010 – Nov 2011"
)

ax.set_xlabel("Month")
ax.set_ylabel("Share of Monthly Revenue (%)")

ax.set_ylim(0, 100)

ax.legend(
    loc="upper left",
    bbox_to_anchor=(1.01, 1)
)

plt.xticks(rotation=45)

plt.tight_layout()

# Save chart
output = ROOT / "assets/customer_revenue_segmentation.png"

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

plt.savefig(
    output,
    dpi=180,
    bbox_inches="tight"
)

print(f"Chart saved: {output}")

plt.close()
