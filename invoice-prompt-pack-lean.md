# Invoice Auto-Entry: Lean Prompt Pack (v2, real-world version)

Nov 9, 2026 · @Heinrich

## How this version works

This is how you would brief a coding assistant on a real project. The rules live once in a project file, the spec lives once in a second file, and each prompt is a few lines. The assistant interviews you for the PRD and decides the details. There is one prompt per phase.

Every box in this pack is one message to copy and paste into your AI tool, or one file to create. Text outside the boxes is for you, not for the AI.

Use a new session for each prompt. The project files carry the context, so every prompt starts by telling the AI to read them.

Trade-off: results vary more between runs than in the full pack. You trade guaranteed identical output for speed and for practice at directing an AI.

## Setup: create these two files in the project folder first

Also make sure these folders from your instructor are in the project folder: `samples/` (5 demo invoice PDFs) and `error-samples/` (error sample PDFs, never edited).

### File 1: CLAUDE.md (project rules, written once)

Name it CLAUDE.md if your tool reads that name. Otherwise paste it at the start of the chat.

```
# Project rules

- I am a non-technical business person. Explain in plain English. Keep code simple and commented.
- Read fields.md for the spec. Read PRD.md once it exists.
- Extraction uses pdfplumber and plain Python rules only. No AI or LLM API, ever.
- Playwright runs as a separate process called from Streamlit with subprocess. Never inside Streamlit.
- Never edit, rename, or delete files in samples/ or error-samples/.
- Never hardcode values from sample invoices into code. Fixes must be general rules.
- Never say something works or is fixed until you ran it and showed me the real output.
- Never use force push, never ask for passwords or tokens, use repository-local git settings only.
- Ask me questions only when the answer changes what you build. Ask at most 3 at a time, as a numbered list. Otherwise assume and tell me the assumption in your reply.
- Only add features that are in PRD.md. Anything else goes to "Later".
- Keep replies short: what you did, what I should look at, what comes next.
```

### File 2: fields.md (the spec, written once)

```
# Invoice Auto-Entry spec

## Portal (already exists, do not rebuild)
URL: https://invoice-entry-demo.vercel.app/
- Page "New invoice" has a form. Page "Saved invoices" lists saved records.
- Dates use a date picker. Amounts are plain whole numbers in IDR.
- Line items: 5 rows available. A row must be completely filled or completely empty.
- Buttons: "Save invoice" and "Clear form".
- Find selectors by inspecting the live portal with Playwright. Do not guess selectors.

## Header fields (form field | label in the PDF)
invoice_number | Nomor Faktur
po_number | Nomor PO
invoice_date | Tanggal Faktur (DD/MM/YYYY in PDF)
due_date | Jatuh Tempo (DD/MM/YYYY in PDF)
payment_terms | Syarat Pembayaran
vendor_name | company name at the top of the document
vendor_tax_id | NPWP
vendor_address | address under the vendor name
bill_to_name | Ditagihkan kepada
bank | Informasi Pembayaran, "Bank:"
account_number | No. Rekening

## Line items (3 to 5 rows per invoice)
description, quantity (integer), unit, unit_price (IDR integer), line_total (IDR integer)

## Totals
subtotal, vat_amount (PPN 11%), total (Total Tagihan)

## Data rules
- PDF amounts look like "Rp 1.040.000". Store as the integer 1040000.
- PDF dates are DD/MM/YYYY. The portal date picker needs YYYY-MM-DD. Convert before entering.
- PDF labels are Indonesian. Portal labels are English.
- Multi-line vendor address: join lines with a comma and a space. No double commas.
- A line item row with no unit gets the placeholder "unit" plus a warning.

## Behavior rules
- Statuses: Ready, Needs review, Sent, Failed.
- Needs review if a field is missing or numbers do not add up (line totals vs subtotal, quantity x unit price vs line total, subtotal + VAT vs total).
- Needs review invoices cannot be sent until the user ticks "I checked this invoice".
- An invoice is Sent only if the portal's "Saved invoices" count goes up by exactly 1.
- One failed invoice must not stop the others.
- Nothing is skipped silently. Every missing or unreadable value becomes a plain-English warning.
```

## Prompt 1: PRD

Answer the assistant's questions (up to 5), then it writes PRD.md.

```
Write PRD.md for this project. Ask me up to 5 questions first, then write it.

Problem: our accounts payable team retypes vendor invoice PDFs into an internal web portal by hand. It is slow and typo-prone.

Build: a local Streamlit app. Upload PDFs, extract fields with pdfplumber (no LLM), review and correct on screen, then enter the data into the portal with Playwright in a visible browser, and show a result per invoice.

Inputs: fields.md (spec), samples/ (5 invoices, used in all phases), error-samples/ (used only in Phase 3).

Your questions must cover: who uses it and how many invoices per week, how long one invoice takes by hand today, the target time and accuracy, and anything I want later but not now.

Sections: problem and goal, users, scope (must have v1, later, out of scope), user flow, functional requirements, data (copy the field table and rules from fields.md), tech and constraints, phases, success metrics, risks and assumptions.

Phases: 1) UI with fake data, 2) extraction and portal automation, 3) fix and improve using the error samples, 4) GitHub. For each phase: goal, deliverables, "done when" checks I can verify by looking at the screen (3 to 6), and which steps are mine.

Every requirement must be a yes or no check. Plain English. About 4 pages. Only features I described.
```

## Prompt 2: Build Phase 1 (UI with fake data)

Copy the box below. When it finishes, run the app command it gives you and check the screens before moving on.

```
Read CLAUDE.md, fields.md and PRD.md. Build Phase 1 only: the Streamlit screens with fake placeholder data. No extraction and no automation yet. When done, tell me the exact command to run the app and what to click to see each screen, and show me the evidence for each "done when" check in PRD.md.
```

## Prompt 3: Build Phase 2 (extraction and portal automation)

Copy the box below in a new session, after Phase 1 looks right.

```
Read CLAUDE.md, fields.md and PRD.md, then the existing project files. Phase 1 (the UI with fake data) is already built. Build Phase 2: extraction from the PDFs in samples/, portal automation, and connect both to the existing screens. Inspect the live portal first and build from what you find. When done, send all 5 samples to the portal, tell me the exact command to run the app, and show me the evidence for each "done when" check in PRD.md.
```

## Prompt 4: Fix and improve

Human step first: upload error-samples/error_01_karya_solusi.pdf in the app and look at the review screen yourself. Then copy the box below.

```
Read CLAUDE.md, fields.md and PRD.md, then the existing project files. Phase 3: fix and improve. error-samples/error_01_karya_solusi.pdf has a line item with no unit. The parser skips it and the totals no longer add up. Fix it with a general rule: such a row is still extracted with the placeholder "unit", a plain-English warning is added, and the invoice becomes Needs review. Then check whether any other missing value (in line items or header fields) can be skipped silently, and fix those too. Rerun the error sample and all 5 samples, show the real output, and add what you did to DEBUG_LOG.md. All 5 samples must stay Ready and still send. Maximum 3 attempts per fix, then stop and report.
```

## Prompt 5: Ship to GitHub

Copy the box below. The AI will stop and ask you to create the empty repository. Do that, paste the URL as your next message, and if it asks you to sign in, run the push in your own terminal and type "continue".

```
Read CLAUDE.md and PRD.md, then the existing project files. Phase 4: ship to GitHub. Add README.md (1 page max: what it does, setup for Mac/Linux and Windows, how to run the app, project structure), requirements.txt with pinned versions, and .gitignore (.venv, __pycache__, screenshots, OS files, temp files the app creates). Do not change app code. Then stop and give me the steps to create an empty private repo named invoice-auto-entry at https://github.com/new. After I paste the URL, commit, push, and verify with git status, git log --oneline, and git ls-remote origin. If sign-in is needed, tell me to run the push in my own terminal.
```

## What the lean version drops compared with the full pack

- Per-prompt rule blocks (moved to CLAUDE.md).
- Exact UI layout and exact function names (the assistant decides, you review on screen).
- Step-by-step verification lists (the "done when" checks in PRD.md take their place).
- Fixed final-reply lengths.
