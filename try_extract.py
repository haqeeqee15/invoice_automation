"""
Quick visual check: read every PDF in samples/ and print what was found.

Run with:   python try_extract.py   (with the .venv active)
"""

import glob

from extract import parse_invoice


def money(amount):
    """1040000 -> 'Rp 1.040.000' (or '-' when empty)."""
    if amount in (None, ""):
        return "-"
    return "Rp " + f"{int(amount):,}".replace(",", ".")


for path in sorted(glob.glob("samples/*.pdf")):
    inv = parse_invoice(path)
    print("=" * 70)
    print(f"{inv['file']}   ->   {inv['status']}")
    print("-" * 70)
    for field in ["invoice_number", "po_number", "invoice_date", "due_date",
                  "payment_terms", "vendor_name", "vendor_tax_id", "vendor_address",
                  "bill_to_name", "bank", "account_number"]:
        print(f"  {field:<16} {inv[field]}")
    print(f"  Line items ({len(inv['items'])}):")
    for n, item in enumerate(inv["items"], start=1):
        print(f"    {n}. {item['description']:<36} {item['quantity']:>4} {item['unit']:<8}"
              f" {money(item['unit_price']):>14} {money(item['line_total']):>14}")
    print(f"  {'subtotal':<16} {money(inv['subtotal'])}")
    print(f"  {'vat_amount':<16} {money(inv['vat_amount'])}")
    print(f"  {'total':<16} {money(inv['total'])}")
    for warning in inv["warnings"]:
        print(f"  WARNING: {warning}")
print("=" * 70)
