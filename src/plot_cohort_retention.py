from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

# Load cohort retention data
data = pd.read_csv(
    ROOT / "data/processed/cohort_retention_m1_m3.csv"
)

# Convert rows into a retention matrix
matrix = data.pivot(
    index="cohort",
    columns="month_num",
    values="retention_pct"
).sort_index()

# Create heatmap
fig, ax = plt.subplots(figsize=(9, 6))

heatmap = ax.imshow(
    matrix.values,
    cmap="Blues",
    vmin=0,
    vmax=40,
    aspect="auto"
)

# Labels
ax.set_xticks(range(len(matrix.columns)))
ax.set_xticklabels(
    [f"M{int(col)}" for col in matrix.columns]
)

ax.set_yticks(range(len(matrix.index)))
ax.set_yticklabels(matrix.index)

ax.set_xlabel("Months After First Observed Purchase")
ax.set_ylabel("Customer Cohort")

ax.set_title(
    "Customer Retention by Cohort\n"
    "UCI Online Retail | January–August 2011"
)

# Add retention percentages inside cells
for i in range(len(matrix.index)):
    for j in range(len(matrix.columns)):
        value = matrix.iloc[i, j]

        ax.text(
            j, i,
            f"{value:.1f}%",
            ha="center",
            va="center",
            color="white" if value >= 22 else "black"
        )

fig.colorbar(
    heatmap,
    ax=ax,
    label="Retention Rate (%)"
)

plt.tight_layout()

# Save chart
output = ROOT / "assets/cohort_retention_heatmap.png"
output.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(output, dpi=180, bbox_inches="tight")

print(f"Heatmap saved: {output}")

plt.close()
