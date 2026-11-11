# Invoice Auto-Entry

A small local tool that reads vendor invoice PDFs and enters them into an invoice portal for you.

- Upload one or more invoice PDFs (or load the 5 built-in samples).
- The tool reads all header fields, totals, and line items, and checks that the amounts add up.
- Each invoice is marked **Ready** or **Needs review**, with plain-English warnings. You can edit every value before sending.
- **Send to portal** opens a visible browser that fills in and saves each invoice, one at a time.
- Each invoice then shows **Sent** or **Failed**, with the reason for any failure.

> **Note:** All invoice data in this project is fictional. The portal (https://invoice-entry-demo.vercel.app/) is a demo site.

## Setup (one time)

You need Python 3 and an internet connection. Open a terminal in the project folder.

**Mac / Linux**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

**Windows**
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## How to run

With the virtual environment active, run:
```
streamlit run app.py
```
The app opens in your web browser. Then:

1. **Upload:** choose your invoice PDFs, or click **Load sample invoices**.
2. **Review:** check the values and correct any wrong ones. For an invoice marked Needs review, tick **I checked this invoice**.
3. **Send:** click **Send all invoices to portal** (or **Send selected invoice to portal**). Do not click in the browser window while it works.
4. **Results:** see which invoices were Sent or Failed. Click **Retry failed** to try failed ones again.

## Project structure

- `app.py` – the Streamlit app (upload, review, send, results).
- `extract.py` – reads an invoice PDF with pdfplumber and checks the values.
- `portal.py` – fills in and saves the portal form with Playwright (runs as a separate process).
- `mock_data.py` – fake invoice data from the first design phase.
- `try_extract.py` – quick check: prints what was read from each file in `samples/`.
- `samples/` – 5 demo invoice PDFs.
- `error-samples/` – invoice PDFs with errors, used for testing the warnings.
- `PRD.md` – the product requirements.
- `DEBUG_LOG.md` – problems found during testing and how they were fixed.
- `invoice-prompt-pack-full.md`, `invoice-prompt-pack-lean.md` – the prompts used to build this project.
- `requirements.txt` – the Python packages needed.
