"""Profile UCI Online Retail and export auditable PostgreSQL input."""

import argparse
import json
from pathlib import Path

import pandas as pd


SOURCE_COLUMNS = [
    "InvoiceNo", "StockCode", "Description", "Quantity",
    "InvoiceDate", "UnitPrice", "CustomerID", "Country",
]


def prepare(raw):
    missing = set(SOURCE_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing source columns: {sorted(missing)}")
    raw = raw.loc[:, SOURCE_COLUMNS].copy()
    data = raw.rename(columns={
        "InvoiceNo": "invoice_no", "StockCode": "stock_code",
        "Description": "description", "Quantity": "quantity",
        "InvoiceDate": "invoice_date", "UnitPrice": "unit_price",
        "CustomerID": "customer_id", "Country": "country",
    })
    data.insert(0, "source_row", range(2, len(data) + 2))
    data["is_duplicate"] = raw.duplicated(keep="first").to_numpy()
    for col in ["invoice_no", "stock_code", "customer_id", "country"]:
        data[col] = data[col].astype("string").str.strip().replace("", pd.NA)
    data["invoice_date"] = pd.to_datetime(data["invoice_date"], errors="raise")
    for col in ["quantity", "unit_price"]:
        data[col] = pd.to_numeric(data[col], errors="raise")
    if data[["invoice_no", "stock_code", "invoice_date", "quantity", "unit_price", "country"]].isna().any().any():
        raise ValueError("Required transaction fields contain missing values")
    if (data["quantity"] % 1 != 0).any():
        raise ValueError("Quantity must be an integer")
    data["quantity"] = data["quantity"].astype("int64")
    data["is_cancellation"] = data["invoice_no"].str.upper().str.startswith("C")
    data["has_customer_id"] = data["customer_id"].notna()
    data["eligible_sale"] = (
        ~data["is_duplicate"] & ~data["is_cancellation"]
        & data["quantity"].gt(0) & data["unit_price"].gt(0)
    )
    data["eligible_cancellation"] = (
        ~data["is_duplicate"] & data["is_cancellation"]
        & data["quantity"].lt(0) & data["unit_price"].gt(0)
    )
    report = {
        "source_rows": len(raw),
        "period_start": str(data["invoice_date"].min()),
        "period_end": str(data["invoice_date"].max()),
        "missing_values": {key: int(value) for key, value in raw.isna().sum().items()},
        "duplicate_rows_after_first": int(data["is_duplicate"].sum()),
        "cancellation_rows": int(data["is_cancellation"].sum()),
        "nonpositive_quantity_rows": int(data["quantity"].le(0).sum()),
        "nonpositive_price_rows": int(data["unit_price"].le(0).sum()),
        "eligible_sale_rows": int(data["eligible_sale"].sum()),
        "eligible_cancellation_rows": int(data["eligible_cancellation"].sum()),
        "other_nonduplicate_rows": int((~data["is_duplicate"] & ~data["eligible_sale"] & ~data["eligible_cancellation"]).sum()),
        "note": "Issue counts can overlap. All source rows are preserved. Eligibility is a documented analytical rule, not a correction to the source.",
    }
    return data, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to official Online Retail.xlsx")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    raw = pd.read_excel(args.input, dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"})
    data, report = prepare(raw)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output_dir / "retail_lines.csv.gz", index=False, date_format="%Y-%m-%d %H:%M:%S", compression="gzip")
    (args.output_dir / "quality_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
