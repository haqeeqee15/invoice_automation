"""
Type invoices into the invoice portal with Playwright (a robot browser).

The field names below were found by inspecting the live portal at
https://invoice-entry-demo.vercel.app/ . The robot finds each box by its
visible label (for example "Vendor name"), not by fragile page codes.

This file is started by the app as a separate program, because Streamlit
and Playwright do not work well together in one program (especially on
Windows). You can also run it yourself:

    python portal.py --input in.json --output out.json

in.json  = a list of invoice dictionaries (same format as extract.py makes)
out.json = a list of results: {file, status ("Sent" or "Failed"), message}
"""

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

PORTAL_URL = "https://invoice-entry-demo.vercel.app/"
SCREENSHOT_FOLDER = Path(__file__).parent / "screenshots"
MAX_ROWS = 5   # the portal form has 5 line item rows

# Our field name -> the label of that box on the portal.
TEXT_FIELDS = {
    "invoice_number": "Invoice number",
    "po_number": "PO number",
    "payment_terms": "Payment terms",
    "vendor_name": "Vendor name",
    "vendor_tax_id": "Vendor tax ID",
    "vendor_address": "Vendor address",
    "bill_to_name": "Bill-to name",
    "bank": "Bank",
    "account_number": "Account number",
}
DATE_FIELDS = {
    "invoice_date": "Invoice date",
    "due_date": "Due date",
}
AMOUNT_FIELDS = {
    "subtotal": "Subtotal",
    "vat_amount": "VAT amount",
    "total": "Total",
}
# Our line item column -> the words used in the portal's row labels,
# for example "Item 1 unit price".
ITEM_COLUMNS = {
    "description": "description",
    "quantity": "quantity",
    "unit": "unit",
    "unit_price": "unit price",
    "line_total": "line total",
}


# ---------------------------------------------------------------------
# Data conversions
# ---------------------------------------------------------------------
def to_portal_date(text, field_name):
    """'05/03/2026' (DD/MM/YYYY) -> '2026-03-05' (YYYY-MM-DD)."""
    text = (text or "").strip()
    try:
        return datetime.strptime(text, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{field_name} '{text}' is not a valid date in DD/MM/YYYY")


def to_portal_number(value, field_name):
    """Any whole number (1040000, '1.040.000', 'Rp 1.040.000', 20.0) -> '1040000'."""
    if isinstance(value, float):
        if value != int(value):
            raise ValueError(f"{field_name} '{value}' is not a whole number")
        value = int(value)
    digits = re.sub(r"[^\d]", "", str(value if value is not None else ""))
    if not digits:
        raise ValueError(f"{field_name} is empty")
    return str(int(digits))


def build_form_values(invoice):
    """
    Work out exactly what to type into each portal box, as a list of
    (portal label, text). Everything comes from the invoice dictionary.
    """
    items = invoice.get("items") or []
    if len(items) > MAX_ROWS:
        raise ValueError("More than 5 line items, portal supports 5")

    values = []
    for field, label in TEXT_FIELDS.items():
        values.append((label, str(invoice.get(field) or "").strip()))
    for field, label in DATE_FIELDS.items():
        values.append((label, to_portal_date(invoice.get(field), label)))
    for row, item in enumerate(items, start=1):
        for column, words in ITEM_COLUMNS.items():
            label = f"Item {row} {words}"
            if column in ("description", "unit"):
                text = str(item.get(column) or "").strip()
                # Never send a partly filled row: stop before anything is typed.
                if not text:
                    raise ValueError(f"{label} is empty. Please fill it in before sending")
                values.append((label, text))
            else:
                values.append((label, to_portal_number(item.get(column), label)))
    for field, label in AMOUNT_FIELDS.items():
        values.append((label, to_portal_number(invoice.get(field), label)))
    return values


# ---------------------------------------------------------------------
# Portal steps
# ---------------------------------------------------------------------
def saved_count(page):
    """Read the number in the 'Saved invoices' link at the top of the page."""
    badge = page.get_by_role("link", name="Saved invoices").get_by_test_id("saved-count")
    return int(badge.inner_text().strip())


def take_screenshot(page, invoice):
    """Save a picture of the page into screenshots/ and return its file name."""
    try:
        SCREENSHOT_FOLDER.mkdir(exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(invoice.get("file", "invoice")).stem)
        name = f"{datetime.now():%Y%m%d_%H%M%S}_{safe_name}.png"
        page.screenshot(path=str(SCREENSHOT_FOLDER / name), full_page=True)
        return name
    except Exception:
        return None


def fill_invoice(page, invoice):
    """
    Open the portal, type ONE invoice, check it, and click "Save invoice".
    Returns {file, status, message}. Never raises an error.
    """
    file_name = invoice.get("file", "")
    try:
        # Work out every value first. Bad dates or too many rows stop here,
        # before anything is typed.
        values = build_form_values(invoice)

        page.goto(PORTAL_URL, wait_until="networkidle")

        # Type every value. Dates are typed as YYYY-MM-DD text with fill(),
        # never by clicking the date picker. Unused rows are not touched.
        for label, text in values:
            page.get_by_label(label, exact=True).fill(text)

        # Read back every box and compare with what we typed.
        for label, text in values:
            typed = page.get_by_label(label, exact=True).input_value()
            if typed != text:
                return failed(page, invoice,
                              f"The portal field '{label}' shows '{typed}' instead of "
                              f"'{text}'. Not saved.")

        # Unused rows must be completely empty.
        for row in range(len(invoice.get("items") or []) + 1, MAX_ROWS + 1):
            for words in ITEM_COLUMNS.values():
                label = f"Item {row} {words}"
                if page.get_by_label(label, exact=True).input_value() != "":
                    return failed(page, invoice, f"The portal field '{label}' should be empty. Not saved.")

        # Save, and check that the "Saved invoices" count goes up by exactly 1.
        before = saved_count(page)
        page.get_by_role("button", name="Save invoice").click()
        page.wait_for_timeout(1000)
        after = saved_count(page)

        if after != before + 1:
            # The portal lists its problems in a box at the top of the form.
            problems = ""
            summary = page.locator("#error-summary")
            if summary.is_visible():
                problems = " ".join(summary.inner_text().split())
            reason = f"The portal did not save it (count stayed at {after})."
            if problems:
                reason += f" Portal says: {problems}"
            return failed(page, invoice, reason)

        # The portal also shows "Saved REC-0001: invoice <number> from <vendor>".
        banner = page.locator("#success-banner")
        banner_text = " ".join(banner.inner_text().split()) if banner.is_visible() else ""
        invoice_number = str(invoice.get("invoice_number") or "").strip()
        if invoice_number not in banner_text:
            return failed(page, invoice,
                          "The count went up, but the portal's confirmation message does not "
                          f"mention invoice {invoice_number}. Please check the portal.")
        message = banner_text.replace("Open invoice list", "").strip()
        return {"file": file_name, "status": "Sent", "message": message}

    except Exception as error:
        return failed(page, invoice, f"Error: {str(error).splitlines()[0]}")


def failed(page, invoice, reason):
    """Build a Failed result and save a screenshot of the page."""
    picture = take_screenshot(page, invoice)
    if picture:
        reason += f" (screenshot: screenshots/{picture})"
    return {"file": invoice.get("file", ""), "status": "Failed", "message": reason}


def send_invoices(invoices):
    """
    Open ONE visible browser, type every invoice in order, then show the
    Saved invoices page for 5 seconds and close the browser.
    Returns a list of {file, status, message}, in the same order.
    """
    results = []
    with sync_playwright() as playwright:
        # slow_mo=300 waits 0.3 seconds between steps so you can follow along.
        browser = playwright.chromium.launch(headless=False, slow_mo=300)
        try:
            # ONE context: the portal keeps saved invoices in this browser only.
            context = browser.new_context()
            page = context.new_page()
            for invoice in invoices:
                results.append(fill_invoice(page, invoice))   # never raises

            # Finish on the Saved invoices page so you can see the result.
            try:
                page.get_by_role("link", name="Saved invoices").click()
                page.wait_for_load_state("networkidle")
                time.sleep(5)
            except Exception:
                pass
        finally:
            browser.close()
    return results


# ---------------------------------------------------------------------
# Command line: python portal.py --input in.json --output out.json
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Send invoices to the invoice portal.")
    parser.add_argument("--input", required=True, help="JSON file with a list of invoices")
    parser.add_argument("--output", required=True, help="JSON file to write the results to")
    args = parser.parse_args()

    invoices = json.loads(Path(args.input).read_text(encoding="utf-8"))
    try:
        results = send_invoices(invoices)
    except Exception as error:
        # For example: the browser could not start at all.
        results = [{"file": inv.get("file", ""), "status": "Failed",
                    "message": f"The browser could not run: {str(error).splitlines()[0]}"}
                   for inv in invoices]
    Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False),
                                 encoding="utf-8")
    for r in results:
        print(f"{r['status']:<7} {r['file']}: {r['message']}")


if __name__ == "__main__":
    main()
