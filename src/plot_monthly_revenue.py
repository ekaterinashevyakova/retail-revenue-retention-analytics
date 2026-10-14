from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

# Load monthly metrics
df = pd.read_csv(
    ROOT / "data/processed/monthly_metrics.csv"
)

df = df.sort_values("month").reset_index(drop=True)

# Calculate month-over-month revenue growth
df["mom_growth_pct"] = (
    df["revenue_gbp"].pct_change() * 100
)

# Convert revenue to millions
df["revenue_millions"] = (
    df["revenue_gbp"] / 1_000_000
)

# Create visualization
fig, ax = plt.subplots(figsize=(13, 6))

ax.plot(
    df["month"],
    df["revenue_millions"],
    marker="o",
    linewidth=2.5,
    markersize=7
)

# Add revenue labels
for i, row in df.iterrows():

    ax.annotate(
        f"£{row['revenue_millions']:.2f}M",
        (i, row["revenue_millions"]),
        xytext=(0, 12),
        textcoords="offset points",
        ha="center",
        fontsize=9
    )

# Formatting
ax.set_title(
    "Monthly Revenue Performance\n"
    "UCI Online Retail | December 2010 – November 2011",
    fontsize=15,
    pad=20
)

ax.set_xlabel("Month")
ax.set_ylabel("Sales Value (£ millions)")

ax.grid(
    axis="y",
    alpha=0.25
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.xticks(rotation=45)

ax.set_ylim(
    0,
    df["revenue_millions"].max() * 1.2
)

plt.tight_layout()

# Save chart
output = ROOT / "assets/monthly_revenue_growth.png"

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

plt.savefig(
    output,
    dpi=180,
    bbox_inches="tight"
)

plt.close()

# Save monthly metrics summary
summary = ROOT / "reports/monthly_revenue_summary.csv"

df[
    [
        "month",
        "revenue_gbp",
        "orders",
        "aov_gbp",
        "mom_growth_pct"
    ]
].to_csv(
    summary,
    index=False,
    float_format="%.4f"
)

print(f"Chart saved: {output}")
print(f"Metrics saved: {summary}")

print("\nMonthly revenue growth:")
print(
    df[
        ["month", "revenue_gbp", "mom_growth_pct"]
    ].round(2).to_string(index=False)
)
