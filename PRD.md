# PRD: Invoice PDF to Portal Entry Tool

## 1. Problem and goal

**Problem.** The accounts payable team receives vendor invoices as PDF files. An employee reads each PDF and types the values into the internal web portal by hand: 14 header and total fields plus 3 to 5 line item rows (5 columns each) per invoice. This is slow and repetitive, and it leads to typos.

**Goal.** Build a small local tool that reads the invoice PDFs, lets the user check and correct the values, and then enters the data into the portal automatically. The aim is less time per invoice and no wrong values saved.

## 2. Users

- **Who:** 2 people in the accounts payable team. They have no coding skills.
- **Volume:** about 20 invoices per week.
- **Today:** about 6 minutes per invoice, typed by hand.
- **What they need:** upload PDFs, check the values on one screen, click one button, and see clearly which invoices were saved and which were not.

## 3. Scope

**Must have (v1)**
- Upload one or more invoice PDFs in a local Streamlit web app.
- Read all fields from each PDF with pdfplumber and simple parsing rules.
- A review screen where every value can be edited, with a status for each invoice.
- Send invoices to the portal with a Playwright script in a visible browser.
- A result for each invoice: Sent or Failed, with the reason.

**Later (ideas for after v1, not built now)**
- Support for other vendors' invoice layouts.
- Scanned PDFs, read with OCR.
- Exporting the results to a file.

**Out of scope**
- Deployment or hosting.
- User accounts or login.
- A database.
- Scanned or image PDFs, and OCR.
- Invoices in other vendors' layouts beyond the 5 samples.
- Editing or deleting invoices already saved in the portal.
- Any extraction based on AI or an LLM.

## 4. User flow

1. The user starts the app and opens it in their web browser.
2. The user uploads one or more invoice PDFs in the upload area.
3. The app reads each PDF and shows the values in a review table. Each invoice gets a status: **Ready** or **Needs review**. Any warnings are shown in plain English.
4. The user checks the values and corrects any wrong ones directly in the table.
5. For each invoice marked Needs review, the user ticks "I checked this invoice".
6. The user clicks **Send to portal**.
7. A browser window opens. The user watches the forms being filled and saved, one invoice at a time.
8. The results area shows each invoice as **Sent** or **Failed**, with the reason for any failure.

## 5. Functional requirements

Each requirement can be checked with a yes or no.

**Upload and extraction**
- FR1. The user can upload one or more PDF files in a single action.
- FR2. For each uploaded PDF, the app extracts all 14 header and total fields and every line item row listed in section 6.
- FR3. Extraction uses pdfplumber and parsing rules only. No AI or LLM service is called.
- FR4. Amounts are stored as plain whole numbers, for example "Rp 1.040.000" becomes 1040000.
- FR5. A vendor address that spans several lines is joined into one line with ", " between the parts.
- FR6. A line item row with no unit is still extracted, with "unit" as its unit, and a warning is shown.
- FR7. No field or line item is skipped without notice. Anything missing or unreadable produces a plain-English warning on screen.

**Status and review**
- FR8. Each invoice shows exactly one status: Ready, Needs review, Sent, or Failed.
- FR9. An invoice is marked Needs review if any field is missing, or if any of these checks fails:
  - quantity × unit price = line total, for every row
  - the sum of the line totals = subtotal
  - subtotal + VAT = total
- FR10. An invoice that passes all the checks in FR9 and has no missing fields is marked Ready.
- FR11. The user can edit every extracted value in the review table before sending.
- FR12. An invoice marked Needs review cannot be sent until the user ticks "I checked this invoice" for it.

**Sending to the portal**
- FR13. Clicking "Send to portal" opens a visible browser and fills the "New invoice" form for each invoice that is allowed to be sent.
- FR14. Dates are entered in the portal as YYYY-MM-DD, converted from the PDF's DD/MM/YYYY.
- FR15. Line item rows are filled from the top down. Unused rows are left completely empty, and no row is left partly filled.
- FR16. The script pauses briefly between steps so the user can follow along.
- FR17. An invoice is marked Sent only if the count on the portal's "Saved invoices" page goes up by exactly 1 after saving it. Otherwise it is marked Failed.
- FR18. A failed invoice does not stop the remaining invoices from being sent.
- FR19. The portal step runs in a separate process from the web app. If the browser closes or errors, the app stays open and shows Failed with a reason.
- FR20. The results area shows each invoice's number, its result (Sent or Failed), and the reason for any failure in plain English.

## 6. Data specification

**Header fields (one value per invoice)**

| Portal field | Label in the PDF (Indonesian) | Format stored |
|---|---|---|
| invoice_number | Nomor Faktur | text |
| po_number | Nomor PO | text |
| invoice_date | Tanggal Faktur (DD/MM/YYYY) | date, sent as YYYY-MM-DD |
| due_date | Jatuh Tempo (DD/MM/YYYY) | date, sent as YYYY-MM-DD |
| payment_terms | Syarat Pembayaran | text |
| vendor_name | Company name at the top of the document | text |
| vendor_tax_id | NPWP | text |
| vendor_address | Address under the vendor name | text, lines joined with ", " |
| bill_to_name | Ditagihkan kepada | text |
| bank | Informasi Pembayaran, "Bank:" | text |
| account_number | No. Rekening | text |

**Totals (one value per invoice)**

| Portal field | Label in the PDF | Format stored |
|---|---|---|
| subtotal | Subtotal | whole number (IDR) |
| vat_amount | PPN 11% | whole number (IDR) |
| total | Total Tagihan | whole number (IDR) |

**Line items (3 to 5 rows per invoice; the portal has 5 rows)**

| Portal column | Format stored |
|---|---|
| description | text |
| quantity | whole number |
| unit | text ("unit" if missing, with a warning) |
| unit_price | whole number (IDR) |
| line_total | whole number (IDR) |

**Data rules**
- Amounts: remove "Rp", spaces, and the thousands dots. "Rp 1.040.000" becomes 1040000.
- Dates: the PDF uses DD/MM/YYYY and the portal date picker needs YYYY-MM-DD. For example, 05/03/2026 becomes 2026-03-05.
- Labels: the PDF labels are in Indonesian and the portal labels are in English. The mapping is the table above.
- Address: if the address spans several lines, join them with a comma and a space, for example "Jl. Contoh No. 1, Kota 12345".
- Line items: each portal row is either completely filled or completely empty.

## 7. Tech stack and constraints

- **Language:** Python.
- **App screens:** Streamlit, running locally on the user's computer.
- **PDF reading:** pdfplumber, with simple parsing rules.
- **Portal automation:** Playwright with Chromium, in a visible (not hidden) browser.
- **Portal:** https://invoice-entry-demo.vercel.app/ already exists and is not rebuilt. The tool uses its "New invoice" page, its "Saved invoices" page, and the "Save invoice" and "Clear form" buttons.
- **Constraints:** runs locally only, with no database, no login, and no AI or LLM API.
- **Inputs:** samples/ holds 5 demo invoice PDFs and is used in all phases. error-samples/ holds error PDFs, is used only in Phase 3, and its files are never edited.

## 8. Phases

### Phase 1: Design the UI
- **Goal:** Build the Streamlit screens using fake placeholder data, with no extraction or automation yet.
- **Deliverables:** app.py
- **Done when:**
  - [ ] The app opens in the browser with an upload area.
  - [ ] A review table shows placeholder invoices, and its values can be edited.
  - [ ] The table has a status column that shows Ready and Needs review examples.
  - [ ] A "Send to portal" button is visible.
  - [ ] A results area shows example Sent and Failed rows, each with a reason.
- **AI agent:** builds the screens. **Human:** opens the app and checks the screens against this list.

### Phase 2: Build the automation
- **Goal:** Make the app really read the PDFs and fill in the portal.
- **Steps:**
  - a) Set up the project: create a Python virtual environment, install streamlit, playwright, and pdfplumber, then run "playwright install chromium".
  - b) Build the extraction function: a PDF goes in and structured data comes out.
  - c) Inspect the live portal with Playwright to find the real form fields, labels, and buttons. **The Playwright script is built from this inspection of the live portal, not from guessed selectors.**
  - d) Turn the findings into a reusable function that takes one invoice's data and fills in the portal. It applies the data conversions from section 6 and runs in a visible browser with a small delay between steps.
  - e) Connect extraction and portal filling to the Streamlit buttons.
- **Deliverables:** app.py, extractor.py, portal.py, and a .venv folder (local only).
- **Done when:**
  - [ ] Uploading the 5 files from samples/ shows 5 invoices, all marked Ready.
  - [ ] The values in the review table match the values printed in each PDF.
  - [ ] Clicking "Send to portal" opens a visible browser that fills and saves each invoice.
  - [ ] All 5 invoices show Sent, and the "Saved invoices" count went up by 5.
  - [ ] The dates in the portal match the PDF dates, and the amounts have no "Rp" or dots.
- **AI agent:** does steps a to e. **Human:** watches the browser run and compares a few saved invoices with their PDFs.

### Phase 3: Fix and improve
- **Goal:** Make extraction handle the error samples without skipping anything silently.
- **Steps:**
  - a) Run the PDFs in error-samples/ through the app and find what goes wrong. The known case: a line item row with no unit is skipped, so the line totals no longer add up.
  - b) Fix the problems with general parsing rules, never with values copied from a sample. A row without a unit is still extracted with "unit" as its unit and a warning, and the invoice becomes Needs review. Anything missing or unreadable produces a plain-English warning.
  - c) After every fix, check that all 5 samples in samples/ are still Ready and still send successfully.
  - d) Record every problem and fix in DEBUG_LOG.md.
- **Deliverables:** updated extractor.py and app.py, and DEBUG_LOG.md.
- **Done when:**
  - [ ] Each error sample shows Needs review with a plain-English warning, and none is silently wrong.
  - [ ] The row with no unit appears in the table with "unit" as its unit.
  - [ ] A Needs review invoice cannot be sent until "I checked this invoice" is ticked.
  - [ ] All 5 files in samples/ are still Ready and still show Sent.
  - [ ] DEBUG_LOG.md lists each problem found and how it was fixed.
- **AI agent:** runs the tests, makes the fixes, and writes the log. **Human:** uploads the error samples and confirms the warnings make sense.

### Phase 4: Upload to GitHub
- **Goal:** Publish the finished project to a GitHub repository.
- **Deliverables:** README.md (what the tool does and how to run it), requirements.txt, and .gitignore.
- **Done when:**
  - [ ] The repository on github.com shows the code, README.md, requirements.txt, and .gitignore.
  - [ ] The README explains in plain steps how to install and start the app.
  - [ ] The .venv folder and any personal or secret files are not in the repository.
  - [ ] The latest commit on GitHub matches the local project.
- **Human step:** create the empty repository on github.com and give its URL to the AI agent. **AI agent:** writes the files, commits, and pushes.

## 9. Success metrics

| Metric | Today | Target |
|---|---|---|
| Time per invoice, including review | about 6 minutes | under 2 minutes |
| Wrong values saved to the portal | not measured | 0 |
| Sample invoices fully correct and Sent | — | 5 of 5 |
| Error samples flagged Needs review with a warning | — | all of them |
| Weekly volume handled | about 20 invoices, typed by hand | about 20 invoices, sent by the tool |

## 10. Risks and assumptions

**Risks**
- **The portal changes its layout or field names.** The script would then fail. Mitigation: each invoice shows Failed with a reason instead of saving wrong data, and the script can be rebuilt by inspecting the portal again.
- **A new vendor layout is not parsed correctly.** Mitigation: the total checks and the warnings flag the invoice as Needs review.
- **The portal is slow or offline.** Mitigation: the invoice shows Failed with a reason, the other invoices continue, and the app stays open.
- **The user ticks "I checked this invoice" without really checking.** Mitigation: the warnings are clear and shown next to the invoice. The final responsibility stays with the user.

**Assumptions**
- The 14 "header and total fields" are the 11 header fields plus subtotal, VAT, and total.
- Every invoice is in the same layout as the 5 samples, and every PDF is text based, not scanned.
- The portal needs no login, and the tool may save test records to it.
- Each user runs the tool on their own Windows or Mac computer with Python installed and internet access.
- Today's error rate for manual entry is unknown, so the accuracy baseline is "not measured".
- A small delay means about half a second between portal actions, which still fits the under-2-minute target.
- If the browser crashes partway through an invoice, that invoice is marked Failed. The user checks the "Saved invoices" page before sending it again.
- An invoice that still fails a total check after the user edits it can be sent only once "I checked this invoice" is ticked.
