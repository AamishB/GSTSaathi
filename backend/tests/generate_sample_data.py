"""
Generate sample data for Phase 6 testing.
Creates:
- tests/sample_data/invoices.csv
- tests/sample_data/gstr2b.json
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import csv
import json
import random


OUTPUT_DIR = Path(__file__).resolve().parent / "sample_data"


SUPPLIERS = [
    ("29ABCDE1234F1Z5", "Alpha Traders"),
    ("27PQRSX5678H1Z2", "Metro Supply Co"),
    ("33LMNOP9012Q1Z8", "Southline Distributors"),
    ("07AAACB2894G1ZJ", "Delhi Industrial Parts"),
    ("24AABCU9603R1ZX", "Gujarat Components"),
]


def random_invoice_number(i: int) -> str:
    return f"INV-2026-{i:05d}"


def generate_invoices(count: int = 1000):
    rows = []
    start_dt = date(2026, 1, 1)

    for i in range(1, count + 1):
        supplier_gstin, supplier_name = random.choice(SUPPLIERS)
        invoice_date = start_dt + timedelta(days=random.randint(0, 89))
        taxable_value = round(random.uniform(5000, 250000), 2)
        gst_rate = random.choice([0, 5, 12, 18, 28])
        tax_value = round(taxable_value * gst_rate / 100, 2)

        igst = tax_value if random.choice([True, False]) else 0
        cgst = round(tax_value / 2, 2) if igst == 0 else 0
        sgst = round(tax_value / 2, 2) if igst == 0 else 0

        row = {
            "invoice_number": random_invoice_number(i),
            "invoice_date": invoice_date.isoformat(),
            "supplier_gstin": supplier_gstin,
            "supplier_name": supplier_name,
            "recipient_gstin": "29ABCDE9999A1Z2",
            "recipient_name": "GSTSaathi Demo Company",
            "taxable_value": taxable_value,
            "igst": igst,
            "cgst": cgst,
            "sgst": sgst,
            "total_value": round(taxable_value + igst + cgst + sgst, 2),
            "hsn_code": random.choice(["8471", "8504", "8517", "3923", "4011"]),
            "place_of_supply": random.choice(["29", "27", "33", "07", "24"]),
        }
        rows.append(row)

    # Add a few intentional duplicate rows for F04 testing.
    rows.extend(rows[10:20])

    # Add a few invalid GSTIN rows for F02 testing.
    for idx in range(5):
        rows[idx]["supplier_gstin"] = f"INVALIDGSTIN{idx}"

    return rows


def generate_gstr2b_from_invoices(invoices, match_ratio: float = 0.8):
    selected = random.sample(invoices, int(len(invoices) * match_ratio))
    entries = []

    for inv in selected:
        entry = {
            "supplier_gstin": inv["supplier_gstin"],
            "invoice_number": inv["invoice_number"],
            "invoice_date": inv["invoice_date"],
            "taxable_value": inv["taxable_value"],
            "igst": inv["igst"],
            "cgst": inv["cgst"],
            "sgst": inv["sgst"],
            "itc_eligible": random.choice([True, True, True, False]),
            "itc_ineligible_reason": None,
        }

        if not entry["itc_eligible"]:
            entry["itc_ineligible_reason"] = random.choice([
                "blocked_credit_section_17_5",
                "personal_use",
                "insufficient_documentation",
            ])

        # Introduce value mismatches in a subset.
        if random.random() < 0.1:
            entry["taxable_value"] = round(entry["taxable_value"] * random.uniform(0.95, 1.05), 2)

        entries.append(entry)

    return entries


def write_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    random.seed(42)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    invoices = generate_invoices(1000)
    gstr2b = generate_gstr2b_from_invoices(invoices, 0.8)

    invoices_path = OUTPUT_DIR / "invoices.csv"
    gstr2b_path = OUTPUT_DIR / "gstr2b.json"

    write_csv(invoices_path, invoices)
    with gstr2b_path.open("w", encoding="utf-8") as f:
        json.dump(gstr2b, f, indent=2)

    print(f"Generated: {invoices_path}")
    print(f"Generated: {gstr2b_path}")
    print(f"Invoices: {len(invoices)}")
    print(f"GSTR-2B Entries: {len(gstr2b)}")


if __name__ == "__main__":
    main()
