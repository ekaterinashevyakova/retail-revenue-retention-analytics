from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

# Load data
df = pd.read_csv(
    ROOT / "data/processed/country_revenue.csv"
)

# Improve country labels for portfolio readers
df["country"] = df["country"].replace({
    "EIRE": "Ireland (EIRE)"
})

# Prepare datasets
top_countries = df.nlargest(
    10, "revenue_gbp"
)

international = df[
    df["country"] != "United Kingdom"
].nlargest(
    10, "revenue_gbp"
)

charts = [
    (
        top_countries,
        "Top 10 Countries by Revenue",
        "top_countries_revenue.png"
    ),
    (
        international,
        "Top 10 International Markets (Excluding UK)",
        "top_international_markets.png"
    )
]

for data, title, filename in charts:

    data = data.sort_values("revenue_gbp")

    fig, ax = plt.subplots(figsize=(11, 6))

    values = data["revenue_gbp"] / 1_000_000

    bars = ax.barh(
        data["country"],
        values
    )

    ax.set_title(
        title + "\nUCI Online Retail | Dec 2010 – Nov 2011"
    )

    ax.set_xlabel("Sales Value (£ millions)")
    ax.set_ylabel("Country")

    ax.set_xlim(
        0,
        values.max() * 1.35
    )

    # Add revenue labels
    labels = [
        f"£{value:,.0f}"
        for value in data["revenue_gbp"]
    ]

    ax.bar_label(
        bars,
        labels=labels,
        padding=4,
        fontsize=9
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    output = ROOT / "assets" / filename

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
