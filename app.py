"""
Invoice Auto-Entry.

1. Upload invoice PDFs (or load the samples).
2. The app reads each PDF (extract.py) and shows the values.
3. You check and correct the values.
4. The app sends them to the invoice portal (portal.py, in a separate process).

Start the app with:   streamlit run app.py
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st

from extract import FIELD_NAMES, missing_field_warning, parse_invoice, validate_invoice

# The folder this file is in, so paths work wherever the app is started.
HERE = Path(__file__).parent
SAMPLES_FOLDER = HERE / "samples"


# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
st.set_page_config(page_title="Invoice Auto-Entry", layout="wide")

# Colour used for each status. Streamlit draws these as coloured labels.
STATUS_COLORS = {
    "Ready": "green",
    "Needs review": "yellow",
    "Sent": "blue",
    "Failed": "red",
}


# ---------------------------------------------------------------------
# Small helper functions
# ---------------------------------------------------------------------
def rupiah(amount):
    """Turn a plain number like 1040000 into the text 'Rp 1.040.000'."""
    if amount in (None, ""):
        return "-"
    try:
        return "Rp " + f"{int(amount):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "-"


def status_label(status):
    """Return the status as a coloured label, for example a green 'Ready'."""
    color = STATUS_COLORS.get(status, "gray")
    return f":{color}-badge[{status}]"


def field_warnings(invoice, field):
    """The warning that belongs to one field ('Could not find <name>. ...')."""
    text = missing_field_warning(FIELD_NAMES[field])
    return [w for w in invoice["warnings"] if w == text]


def show_warnings(warnings):
    """Show a short list of warnings in red, right under a field."""
    for warning in warnings:
        st.markdown(f":red[⚠ {warning}]")


def text_field(invoice, index, field, label):
    """Show one editable text box, save what the user types, show its warning."""
    invoice[field] = st.text_input(label, value=invoice[field] or "", key=f"{index}_{field}")
    show_warnings(field_warnings(invoice, field))


def amount_field(invoice, index, field, label):
    """Show one editable whole-number box with the Rupiah amount beside it."""
    left, right = st.columns([2, 1], vertical_alignment="bottom")
    with left:
        value = invoice[field]
        invoice[field] = st.number_input(
            label, value=None if value in (None, "") else int(value),
            min_value=0, step=1, format="%d", key=f"{index}_{field}",
        )
    with right:
        st.markdown(f"**{rupiah(invoice[field])}**")
    show_warnings(field_warnings(invoice, field))


def load_pdfs(paths, names):
    """Read each PDF and keep the results in the session memory."""
    st.session_state.invoices = [parse_invoice(str(p)) for p in paths]
    # Show the original file name (uploads are saved under a temp name).
    for invoice, name in zip(st.session_state.invoices, names):
        invoice["file"] = name
    st.session_state.results = {}
    st.session_state.checked = {}
    st.session_state.notice = None


def send_to_portal(indexes):
    """
    Send the chosen invoices (by position) to the portal, using the values
    currently in the review form, including any corrections.

    The browser robot (portal.py) runs as a separate program. We give it
    the invoices in a temporary JSON file and read its results back.
    """
    invoices = st.session_state.invoices
    checked = st.session_state.checked

    # Check each invoice again with its edited values, then block any
    # "Needs review" invoice that has not been ticked as checked.
    allowed, blocked = [], []
    for i in indexes:
        validate_invoice(invoices[i])
        if invoices[i]["warnings"] and not checked.get(i, False):
            blocked.append(i)
        else:
            allowed.append(i)

    if blocked:
        names = ", ".join(invoices[i]["file"] for i in blocked)
        # Kept in memory so the message is still visible after the page refreshes.
        st.session_state.notice = (
            f"Not sent: {names}. These invoices need review. Choose each one above, "
            "check the values, and tick **I checked this invoice**."
        )
    else:
        st.session_state.notice = None
    if not allowed:
        st.rerun()

    with tempfile.TemporaryDirectory() as folder:
        in_file = os.path.join(folder, "in.json")
        out_file = os.path.join(folder, "out.json")
        # Send a copy without the app-only helper fields.
        to_send = []
        for i in allowed:
            data = copy.deepcopy(invoices[i])
            for helper in ("status", "warnings", "extract_warnings"):
                data.pop(helper, None)
            to_send.append(data)
        with open(in_file, "w", encoding="utf-8") as f:
            json.dump(to_send, f, ensure_ascii=False, default=str)

        with st.spinner(f"Sending {len(allowed)} invoice(s). A browser window opens, "
                        "please do not click in it..."):
            try:
                run = subprocess.run(
                    [sys.executable, str(HERE / "portal.py"), "--input", in_file,
                     "--output", out_file],
                    cwd=str(HERE), capture_output=True, text=True, timeout=900,
                )
                with open(out_file, encoding="utf-8") as f:
                    run_results = json.load(f)
            except Exception as error:
                # The robot crashed or never wrote its results: mark all Failed.
                details = ""
                if "run" in locals() and run.stderr:
                    details = " " + run.stderr.strip().splitlines()[-1]
                run_results = [{"status": "Failed",
                                "message": f"The portal program did not finish ({error}).{details}"}
                               for _ in allowed]

    # Results come back in the same order the invoices were sent.
    for i, result in zip(allowed, run_results):
        st.session_state.results[i] = {"status": result["status"], "message": result["message"]}
        invoices[i]["status"] = result["status"]

    # Run the page again so every table shows the new statuses.
    st.rerun()


# ---------------------------------------------------------------------
# Memory that survives page refreshes (Streamlit "session state")
# ---------------------------------------------------------------------
if "invoices" not in st.session_state:
    st.session_state.invoices = []    # the invoices and all the user's edits
if "results" not in st.session_state:
    st.session_state.results = {}     # invoice position -> {status, message}
if "checked" not in st.session_state:
    st.session_state.checked = {}     # invoice position -> "I checked this invoice"
if "notice" not in st.session_state:
    st.session_state.notice = None    # message about invoices that were not sent
if "upload_signature" not in st.session_state:
    st.session_state.upload_signature = None


# ---------------------------------------------------------------------
# Top of the page
# ---------------------------------------------------------------------
st.title("Invoice Auto-Entry")
st.caption("Upload vendor invoices, check the values, and send them to the invoice portal.")


# ---------------------------------------------------------------------
# Section 1: Upload
# ---------------------------------------------------------------------
st.header("1. Upload")
with st.container(border=True):
    upload_col, button_col = st.columns([3, 1], vertical_alignment="center")
    with upload_col:
        uploaded_files = st.file_uploader(
            "Choose one or more invoice PDF files",
            type=["pdf"],
            accept_multiple_files=True,
        )
    with button_col:
        st.write("No files at hand?")
        samples_clicked = st.button("Load sample invoices", width="stretch")

# New uploads: save them to a temporary folder and read them.
# The "signature" makes sure the same files are only read once.
if uploaded_files:
    signature = [(f.name, f.size) for f in uploaded_files]
    if signature != st.session_state.upload_signature:
        st.session_state.upload_signature = signature
        with st.spinner("Reading the PDF files..."):
            temp_folder = Path(tempfile.mkdtemp(prefix="invoices_"))
            paths = []
            for number, f in enumerate(uploaded_files):
                path = temp_folder / f"{number}_{f.name}"
                path.write_bytes(f.getvalue())
                paths.append(path)
            load_pdfs(paths, [f.name for f in uploaded_files])

if samples_clicked:
    st.session_state.upload_signature = None
    sample_paths = sorted(SAMPLES_FOLDER.glob("*.pdf"))
    with st.spinner("Reading the sample invoices..."):
        load_pdfs(sample_paths, [p.name for p in sample_paths])

invoices = st.session_state.invoices
results = st.session_state.results

# Nothing loaded yet: show a friendly message and stop here.
if not invoices:
    st.write("")
    st.info(
        "No invoices yet. Upload your invoice PDF files above, "
        "or click **Load sample invoices** to use the 5 samples."
    )
    st.stop()


def refresh_status(index):
    """Check one invoice again with its current (edited) values.
    If it was already sent, its status shows the send result instead."""
    invoice = invoices[index]
    validate_invoice(invoice)
    if index in results:
        invoice["status"] = results[index]["status"]


# ---------------------------------------------------------------------
# Section 2: Review extracted data
# ---------------------------------------------------------------------
st.header("2. Review extracted data")

# --- Choose one invoice to review -----------------------------------
selected = st.selectbox(
    "Choose an invoice to review",
    options=list(range(len(invoices))),
    format_func=lambda i: f"{invoices[i]['file']}  ({invoices[i]['invoice_number'] or 'no number'})",
    key="selected_invoice",
)
invoice = invoices[selected]

# The status and warnings shown at the top are filled in further down,
# after the edit boxes, so they always reflect the latest corrections.
status_area = st.container()

# --- Header fields, in two columns ----------------------------------
with st.expander("Invoice header", expanded=True):
    left, right = st.columns(2)
    with left:
        st.subheader("Invoice details", divider="gray")
        text_field(invoice, selected, "invoice_number", "Invoice number")
        text_field(invoice, selected, "po_number", "PO number")
        text_field(invoice, selected, "invoice_date", "Invoice date (DD/MM/YYYY)")
        text_field(invoice, selected, "due_date", "Due date (DD/MM/YYYY)")
        text_field(invoice, selected, "payment_terms", "Payment terms")

        st.subheader("Bill to", divider="gray")
        text_field(invoice, selected, "bill_to_name", "Bill to")
    with right:
        st.subheader("Vendor", divider="gray")
        text_field(invoice, selected, "vendor_name", "Vendor name")
        text_field(invoice, selected, "vendor_tax_id", "Vendor tax ID (NPWP)")
        text_field(invoice, selected, "vendor_address", "Vendor address")

        st.subheader("Payment", divider="gray")
        text_field(invoice, selected, "bank", "Bank")
        text_field(invoice, selected, "account_number", "Account number")

# --- Line items -----------------------------------------------------
with st.expander("Line items", expanded=True):
    table_col, amounts_col = st.columns([3, 1])
    with table_col:
        st.caption("Click a cell to change it. Amounts are whole numbers without dots.")
        invoice["items"] = st.data_editor(
            invoice["items"],
            key=f"{selected}_items",
            num_rows="fixed",
            hide_index=True,
            width="stretch",
            column_order=["description", "quantity", "unit", "unit_price", "line_total"],
            column_config={
                "description": st.column_config.TextColumn("Description", width="large"),
                "quantity": st.column_config.NumberColumn("Qty", min_value=0, step=1, format="%d"),
                "unit": st.column_config.TextColumn("Unit"),
                "unit_price": st.column_config.NumberColumn(
                    "Unit price (IDR)", min_value=0, step=1, format="%d"),
                "line_total": st.column_config.NumberColumn(
                    "Line total (IDR)", min_value=0, step=1, format="%d"),
            },
        )
    with amounts_col:
        # Read-only copy of the amounts with Indonesian thousand separators.
        st.caption("Amounts in Rupiah (read only)")
        st.dataframe(
            [
                {"Unit price": rupiah(item["unit_price"]), "Line total": rupiah(item["line_total"])}
                for item in invoice["items"]
            ],
            hide_index=True,
            width="stretch",
        )
    line_area = st.container()   # line item warnings, filled in below

# --- Totals ---------------------------------------------------------
with st.expander("Totals", expanded=True):
    left, right = st.columns(2)
    with left:
        amount_field(invoice, selected, "subtotal", "Subtotal (IDR)")
        amount_field(invoice, selected, "vat_amount", "VAT amount (PPN 11%) (IDR)")
        amount_field(invoice, selected, "total", "Total (IDR)")
        totals_area = st.container()   # totals warnings, filled in below

# Now that every edit box has been read, check all invoices again.
for i in range(len(invoices)):
    refresh_status(i)

# Sort the warnings into the place where they are shown.
field_texts = {missing_field_warning(name) for name in FIELD_NAMES.values()}
line_warnings = [w for w in invoice["warnings"]
                 if w.startswith("Line ") or "line item" in w]
total_warnings = [w for w in invoice["warnings"]
                  if w.startswith("Subtotal") or w.startswith("Line totals add up")]
other_warnings = [w for w in invoice["warnings"]
                  if w not in field_texts and w not in line_warnings and w not in total_warnings]
line_warnings = [w for w in line_warnings if w not in total_warnings]

with line_area:
    show_warnings(line_warnings)
with totals_area:
    show_warnings(total_warnings)

with status_area:
    st.markdown(f"Status: {status_label(invoice['status'])}")
    if invoice["warnings"]:
        st.warning(
            f"This invoice has {len(invoice['warnings'])} warning(s). "
            "They are shown in red next to the related value."
        )
        show_warnings(other_warnings)
        # Needs-review invoices can only be sent after this box is ticked.
        st.session_state.checked[selected] = st.checkbox(
            "I checked this invoice",
            value=st.session_state.checked.get(selected, False),
            key=f"{selected}_checked",
        )

# --- Summary table: one row per invoice -----------------------------
st.subheader("All invoices")
with st.container(border=True):
    headings = st.columns([3, 3, 3, 2, 2])
    for column, text in zip(headings, ["File name", "Invoice number", "Vendor", "Total", "Status"]):
        column.markdown(f"**{text}**")
    for inv in invoices:
        row = st.columns([3, 3, 3, 2, 2])
        row[0].write(inv["file"])
        row[1].write(inv["invoice_number"] or "-")
        row[2].write(inv["vendor_name"] or "-")
        row[3].write(rupiah(inv["total"]))
        row[4].markdown(status_label(inv["status"]))


# ---------------------------------------------------------------------
# Section 3: Send to portal
# ---------------------------------------------------------------------
st.header("3. Send to portal")
with st.container(border=True):
    st.caption("A browser window opens and fills in the portal. Please do not click in it.")
    one_col, all_col, _ = st.columns([1, 1, 2])
    send_one = one_col.button("Send selected invoice to portal", width="stretch")
    send_all = all_col.button("Send all invoices to portal", type="primary", width="stretch")

    if st.session_state.notice:
        st.error(st.session_state.notice)

    if send_one:
        send_to_portal([selected])
    if send_all:
        send_to_portal(list(range(len(invoices))))


# ---------------------------------------------------------------------
# Section 4: Results
# ---------------------------------------------------------------------
st.header("4. Results")
with st.container(border=True):
    if not results:
        st.write("No invoices have been sent yet. Results will appear here.")
    else:
        headings = st.columns([3, 2, 5])
        for column, text in zip(headings, ["File name", "Status", "Message"]):
            column.markdown(f"**{text}**")
        for i in sorted(results):
            row = st.columns([3, 2, 5])
            row[0].write(invoices[i]["file"])
            row[1].markdown(status_label(results[i]["status"]))
            row[2].write(results[i]["message"])

        failed = [i for i in sorted(results) if results[i]["status"] == "Failed"]
        if failed:
            st.error(f"{len(failed)} invoice(s) could not be sent.")
            if st.button("Retry failed"):
                send_to_portal(failed)
        else:
            st.success("All sent invoices were saved to the portal.")
