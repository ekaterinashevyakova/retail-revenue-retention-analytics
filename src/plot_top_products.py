from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

# Load product data
df = pd.read_csv(
    ROOT / "data/processed/top_products.csv"
)

# Sort products by revenue
df = df.sort_values("revenue_gbp").copy()

# Create descriptive labels
df["label"] = (
    df["product_name"] +
    " (" + df["stock_code"].astype(str) + ")"
)

# Create chart
fig, ax = plt.subplots(figsize=(13, 7))

bars = ax.barh(
    df["label"],
    df["revenue_gbp"]
)

ax.set_title(
    "Top 10 Merchandise Candidates by Sales Value\n"
    "UCI Online Retail | Dec 2010 – Nov 2011",
    fontsize=15,
    pad=20
)

ax.set_xlabel("Sales Value (£)")
ax.set_ylabel("Product")

# Add revenue labels
labels = [
    f"£{value:,.0f}"
    for value in df["revenue_gbp"]
]

ax.bar_label(
    bars,
    labels=labels,
    padding=5,
    fontsize=9
)

ax.set_xlim(
    0,
    df["revenue_gbp"].max() * 1.25
)

ax.tick_params(axis="y", labelsize=9)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.grid(
    axis="x",
    alpha=0.2
)

ax.set_axisbelow(True)

# Save chart
plt.tight_layout()

output = ROOT / "assets/top_products_revenue.png"

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
