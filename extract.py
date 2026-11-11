"""
Read one invoice PDF and turn it into a Python dictionary.

No AI is used. We read the text of the PDF with pdfplumber and then
look for the Indonesian labels (for example "Nomor Faktur") line by line.

The dictionary has exactly the same field names as mock_data.py, so the
app can show it without changes.

Main functions:
    parse_invoice(pdf_path)   -> reads a PDF, returns one invoice dictionary
    validate_invoice(invoice) -> checks a dictionary (never reads a PDF),
                                 fills in "warnings" and "status"
"""

import os
import re
from datetime import datetime

import pdfplumber


# Every header field, with the plain-English name used in warnings.
# The order here is also the order the warnings appear in.
FIELD_NAMES = {
    "invoice_number": "Invoice number",
    "po_number": "PO number",
    "invoice_date": "Invoice date",
    "due_date": "Due date",
    "payment_terms": "Payment terms",
    "vendor_name": "Vendor name",
    "vendor_tax_id": "Vendor tax ID (NPWP)",
    "vendor_address": "Vendor address",
    "bill_to_name": "Bill to",
    "bank": "Bank",
    "account_number": "Account number",
    "subtotal": "Subtotal",
    "vat_amount": "VAT amount (PPN 11%)",
    "total": "Total",
}

# Column names of a line item, with plain-English names for warnings.
ITEM_NAMES = {
    "description": "description",
    "quantity": "quantity",
    "unit": "unit",
    "unit_price": "unit price",
    "line_total": "line total",
}

# "Label : value" fields. Left: our field name. Right: the PDF label.
LABELLED_FIELDS = {
    "invoice_number": "Nomor Faktur",
    "po_number": "Nomor PO",
    "invoice_date": "Tanggal Faktur",
    "due_date": "Jatuh Tempo",
    "payment_terms": "Syarat Pembayaran",
    "vendor_tax_id": "NPWP",
    "bank": "Bank",
    "account_number": "No. Rekening",
}

# Amount fields. The label must be at the start of the line.
AMOUNT_FIELDS = {
    "subtotal": "Subtotal",
    "vat_amount": "PPN 11%",
    "total": "Total Tagihan",
}

# A Rupiah amount exactly as the PDF prints it: "Rp 52.000", "Rp 1.040.000".
# Groups of 3 digits split by dots. Anything else (for example a comma
# like "Rp 1.250,50") is NOT accepted, so it can never be read wrongly.
AMOUNT = r"Rp\s*\d{1,3}(?:\.\d{3})*"

# One line item row looks like this in the PDF:
#   1 Kertas HVS A4 80 gsm 20 rim Rp 52.000 Rp 1.040.000
#   (row number, description, quantity, unit, unit price, line total)
# The unit is optional, so a row without a unit is still found.
ITEM_ROW = re.compile(
    r"^\d+\s+(?P<description>.+?)\s+(?P<quantity>\d+)\s+"
    r"(?:(?P<unit>[^\d\s]\S*)\s+)?"
    r"(?P<unit_price>" + AMOUNT + r")\s+(?P<line_total>" + AMOUNT + r")$"
)

# Used only when a row does not match ITEM_ROW: the row number at the start.
ROW_START = re.compile(r"^\d+\s+(?P<rest>.*)$")
# The two amounts at the end of a row (unit price, then line total).
TWO_AMOUNTS = re.compile(
    r"^(?P<unit_price>" + AMOUNT + r")\s+(?P<line_total>" + AMOUNT + r")$")
# The text before the amounts: description, then quantity, then unit.
# The quantity must stand alone (so "Cat6" is never read as quantity 6).
ROW_TEXT = re.compile(
    r"^(?P<description>.*?)(?:(?:^|\s+)(?P<quantity>\d+)(?:\s+(?P<unit>[^\d\s]\S*))?)?\s*$")

# Placeholder for a row with no unit (the portal needs every cell filled).
UNIT_PLACEHOLDER = "unit"


def missing_field_warning(name):
    """The warning for a header or total field that is empty."""
    return f"Could not find {name}. Please check the PDF and type it in."


def is_blank(value):
    """True for an empty cell: None, empty text, or 'not a number' (NaN)."""
    if value is None:
        return True
    if isinstance(value, float) and value != value:   # NaN is never equal to itself
        return True
    return str(value).strip() == ""


def to_number(text):
    """Turn money text like 'Rp 1.040.000' into the whole number 1040000.
    Returns None if there are no digits at all."""
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else None


def empty_invoice(file_name):
    """An invoice dictionary with every field present but empty."""
    invoice = {"file": file_name}
    for field in FIELD_NAMES:
        invoice[field] = ""
    invoice["items"] = []
    invoice["subtotal"] = None
    invoice["vat_amount"] = None
    invoice["total"] = None
    invoice["status"] = "Needs review"
    invoice["warnings"] = []
    return invoice


def find_label_value(lines, label):
    """Find 'Label : value' or 'Label: value' and return the value text."""
    pattern = re.compile(r"^" + re.escape(label) + r"\s*:\s*(.*)$")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return ""


def join_address(parts):
    """Join address lines with ', ' without doubling a comma."""
    result = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if not result:
            result = part
        elif result.endswith(","):
            result += " " + part
        else:
            result += ", " + part
    return result


def read_lines(pdf_path):
    """Return every non-empty text line of the PDF, all pages together."""
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines.extend(line.strip() for line in text.splitlines() if line.strip())
    return lines


def parse_lines(invoice, lines):
    """Fill the invoice dictionary from the PDF text lines."""
    # --- Simple "Label : value" fields ------------------------------
    for field, label in LABELLED_FIELDS.items():
        invoice[field] = find_label_value(lines, label)

    # --- Vendor name and address ------------------------------------
    # The vendor name is the first line after the title "FAKTUR (INVOICE)".
    # The address is every line after that, until the phone or NPWP line.
    start = 0
    if lines and lines[0].upper().startswith("FAKTUR"):
        start = 1
    if start < len(lines):
        first = lines[start]
        # Only accept it as a name if it is not already a labelled line.
        if ":" not in first:
            invoice["vendor_name"] = first
            address_parts = []
            for line in lines[start + 1:]:
                if re.match(r"^(Telp|NPWP|Nomor Faktur)\b", line, re.IGNORECASE):
                    break
                address_parts.append(line)
            invoice["vendor_address"] = join_address(address_parts)

    # --- Bill to name: the line after "Ditagihkan kepada:" ----------
    for i, line in enumerate(lines):
        match = re.match(r"^Ditagihkan kepada\s*:\s*(.*)$", line)
        if match:
            same_line = match.group(1).strip()
            if same_line:
                invoice["bill_to_name"] = same_line
            elif i + 1 < len(lines):
                invoice["bill_to_name"] = lines[i + 1]
            break

    # --- Totals -----------------------------------------------------
    # The amount must look exactly like "Rp 1.040.000". If it does not,
    # it is left empty with a warning, instead of guessing a number.
    for field, label in AMOUNT_FIELDS.items():
        for line in lines:
            if line.startswith(label):
                text = line[len(label):].strip()
                if re.fullmatch(AMOUNT, text):
                    invoice[field] = to_number(text)
                else:
                    invoice["warnings"].append(
                        f"{FIELD_NAMES[field]} in the PDF reads \"{text}\", which is not a "
                        "whole Rupiah amount. It was left empty. Please check the PDF.")
                break

    # --- Line items: rows between the table heading and the totals --
    in_table = False
    for line in lines:
        if line.startswith("No Deskripsi"):
            in_table = True
            continue
        # The table ends at the first totals line (normally "Subtotal").
        if any(line.startswith(label) for label in AMOUNT_FIELDS.values()):
            break
        if not in_table:
            continue
        number = len(invoice["items"]) + 1   # the line number this row will get
        match = ITEM_ROW.match(line)
        if match:
            # The normal case: every column was read.
            invoice["items"].append({
                "description": match.group("description").strip(),
                "quantity": int(match.group("quantity")),
                "unit": match.group("unit") or UNIT_PLACEHOLDER,
                "unit_price": to_number(match.group("unit_price")),
                "line_total": to_number(match.group("line_total")),
            })
            if not match.group("unit"):
                invoice["warnings"].append(
                    f"Line {number} has no unit. The placeholder '{UNIT_PLACEHOLDER}' "
                    "was used. Please check the unit in the PDF.")
            continue

        item = read_partial_row(line)
        if item is not None:
            # Some columns could not be read. Keep the row (never skip it),
            # leave those cells empty, and warn. validate_invoice then lists
            # exactly which cells are empty.
            invoice["items"].append(item)
            invoice["warnings"].append(
                f"Line {number} could only be partly read from the PDF: \"{line}\". "
                "The unreadable cells were left empty.")
        else:
            # Not a numbered row at all: say so and show the text.
            invoice["warnings"].append(
                f"Could not read this line item row: \"{line}\". It was not added. "
                "Please compare the line items with the PDF.")


def read_partial_row(line):
    """
    Read a line item row that did not match the normal pattern.
    Only values that can be read safely are filled in; the rest are left
    empty (None). Returns None if the line does not start with a row number.
    """
    start = ROW_START.match(line)
    if not start:
        return None
    rest = start.group("rest")
    item = {key: None for key in ITEM_NAMES}

    # Split the row where the first amount ("Rp" followed by a digit) begins.
    first_amount = re.search(r"\bRp\s*\d", rest)
    text = rest if first_amount is None else rest[:first_amount.start()]
    amounts = "" if first_amount is None else rest[first_amount.start():].strip()

    # Both amounts are taken only if there are exactly two, in the right format.
    # With one amount we cannot tell if it is the unit price or the line total.
    two = TWO_AMOUNTS.match(amounts)
    if two:
        item["unit_price"] = to_number(two.group("unit_price"))
        item["line_total"] = to_number(two.group("line_total"))

    words = ROW_TEXT.match(text.strip())
    if words:
        item["description"] = words.group("description").strip() or None
        if words.group("quantity"):
            item["quantity"] = int(words.group("quantity"))
        item["unit"] = words.group("unit")
    return item


def validate_invoice(invoice):
    """
    Check one invoice dictionary and set its "warnings" and "status".
    This never reads a PDF, so the app can call it again after edits.

    Warnings that came from reading the PDF (for example an unreadable
    row) are kept in "extract_warnings" and added back each time.
    """
    warnings = list(invoice.get("extract_warnings", []))

    # 1. Missing or empty fields.
    for field, name in FIELD_NAMES.items():
        if is_blank(invoice.get(field)):
            warnings.append(missing_field_warning(name))

    # Dates must be real dates written as DD/MM/YYYY (the portal needs this).
    for field in ("invoice_date", "due_date"):
        value = str(invoice.get(field) or "").strip()
        if value:
            try:
                datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                warnings.append(
                    f"{FIELD_NAMES[field]} \"{value}\" is not a valid date in DD/MM/YYYY. "
                    "Please check the PDF and correct it.")

    items = invoice.get("items") or []
    if not items:
        warnings.append("Could not find any line items. Please check the PDF.")

    # 2. Each row: every column filled, and quantity x unit price = line total.
    for number, item in enumerate(items, start=1):
        missing = [name for key, name in ITEM_NAMES.items() if is_blank(item.get(key))]
        if missing:
            warnings.append(
                f"Line {number}: missing {', '.join(missing)}. "
                "Please check this row in the PDF and fill in the empty cells.")
            continue
        try:
            expected = int(item["quantity"]) * int(item["unit_price"])
            if expected != int(item["line_total"]):
                warnings.append(
                    f"Line {number}: quantity x unit price is {expected}, "
                    f"but line total says {int(item['line_total'])}. "
                    "Please check this row in the PDF.")
        except (TypeError, ValueError):
            warnings.append(
                f"Line {number}: quantity or amounts are not whole numbers. "
                "Please check this row in the PDF.")

    # 3. Sum of line totals = subtotal, and subtotal + VAT = total.
    #    The sum is only checked when every line total is filled in;
    #    an empty line total already has its own warning above.
    try:
        all_totals_filled = all(not is_blank(item.get("line_total")) for item in items)
        if items and all_totals_filled and not is_blank(invoice.get("subtotal")):
            line_sum = sum(int(item["line_total"]) for item in items)
            if line_sum != int(invoice["subtotal"]):
                warnings.append(
                    f"Line totals add up to {line_sum}, "
                    f"but Subtotal says {int(invoice['subtotal'])}. "
                    "A line item may be missing or wrong. Please compare with the PDF.")
        if all(not is_blank(invoice.get(f)) for f in ("subtotal", "vat_amount", "total")):
            expected = int(invoice["subtotal"]) + int(invoice["vat_amount"])
            if expected != int(invoice["total"]):
                warnings.append(
                    f"Subtotal + VAT is {expected}, but Total says {int(invoice['total'])}. "
                    "Please check the totals in the PDF.")
    except (TypeError, ValueError):
        warnings.append(
            "Line totals, Subtotal, VAT or Total is not a whole number. Please check the totals.")

    invoice["warnings"] = warnings
    invoice["status"] = "Ready" if not warnings else "Needs review"
    return invoice


def parse_invoice(pdf_path):
    """Read one PDF and return one invoice dictionary. Never crashes."""
    invoice = empty_invoice(os.path.basename(pdf_path))
    try:
        lines = read_lines(pdf_path)
        if not lines:
            invoice["warnings"].append(
                "The PDF has no readable text (it may be a scanned image).")
        else:
            parse_lines(invoice, lines)
    except Exception as error:  # any problem with the file itself
        invoice["warnings"].append(f"Could not read this PDF: {error}")

    # Keep the reading problems so validate_invoice can add them back later.
    invoice["extract_warnings"] = list(invoice["warnings"])
    return validate_invoice(invoice)
