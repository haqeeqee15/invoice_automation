# Invoice Auto-Entry: Full Build Prompt Pack (v2, reliable version)

Nov 9, 2026 · @Heinrich

## How to use this pack

Run the five prompts below in order, all inside the same project folder, because each one builds on the files the previous one created. Prompt 5 stops once and waits for you to type "continue". Every prompt is inside its own box. Copy the whole box and paste it into your AI tool as one message. Text outside the boxes is for you, not for the AI.

Run all five prompts with any coding assistant that can run commands on your own computer. The portal step needs a visible browser, and the GitHub step relies on your own sign-in.

| # | Prompt | Main outputs | Your human step |
| --- | --- | --- | --- |
| 1 | Generate PRD | PRD.md | Edit the BUSINESS FACTS block before pasting |
| 2 | Generate UI, Phase 1 | app.py, mock_data.py | None |
| 3 | Build the Automation, Phase 2 | extract.py, try_extract.py, portal.py, updated app.py, requirements.txt | None |
| 4 | Fix and Improve, Phase 3 | DEBUG_LOG.md, updated extract.py and portal.py | Run the error sample, then copy the prompt and paste it into your AI tool |
| 5 | Upload to GitHub, Phase 4 | README.md, .gitignore, requirements.txt, git commit and push | Create the empty GitHub repository and paste its URL; set your git identity or push yourself if asked |

## Before you start

Before you run Prompt 1, make sure you have these two folders from your instructor inside your project folder:

- A `samples/` folder with the 5 demo invoice PDFs. Used from Prompt 1 onward.
- An `error-samples/` folder with the error sample PDFs. Used in Prompt 4. Do not edit these files.

## Prompt 1: Generate PRD

Human step: in the box below, change the 5 values under BUSINESS FACTS to match your company. Then copy the whole box.

```text
You are a senior product manager helping a non-technical business person write a Product Requirements Document (PRD). Write the PRD for the project described below.

### RULES FOR THIS TASK

- Write ONLY the PRD. Do not write any code and do not install anything in this step.
- Save the PRD as a file named PRD.md in the current project folder.
- Do not ask me questions. If something is unclear, make a reasonable assumption and list it in the "Assumptions" section of the PRD.
- Write in plain English for a non-technical reader. Keep the whole PRD to 5 pages at most. Keep the Phases section compact: one short block per phase. No filler.
- Do not add features, tools, or phases that are not described here. Anything extra goes in "Later" or "Out of scope".
- Every requirement must be testable: someone must be able to check yes or no.

### THE PROBLEM

Our accounts payable team receives vendor invoices as PDF files. An employee reads each PDF and manually types the values into our internal web portal, 14 header and total fields plus 3 to 5 line item rows (5 columns each) per invoice. It is slow, repetitive, and easy to make typos. We want a small tool that reads the PDFs and enters the data into the portal automatically.

### BUSINESS FACTS

Use these facts in the "Users" and "Success metrics" sections. Do not invent any other numbers. If a fact is blank, make an assumption and list it under Assumptions.

- Users: 2 people in the accounts payable team, no coding skills
- Volume: about 20 invoices per week
- Time today: about 6 minutes per invoice by hand
- Time target: under 2 minutes per invoice, including review
- Accuracy target: 0 wrong values saved to the portal

### WHAT WE ARE BUILDING

A local web app built with Streamlit that:

1. Lets the user upload one or more invoice PDFs.
2. Extracts the invoice fields from each PDF using a Python PDF text library (pdfplumber) and simple parsing rules. The PDFs are text based, not scanned. Do NOT use any AI or LLM API for extraction.
3. Shows the extracted data in a review screen where the user can correct values before sending.
4. Sends the data into the portal automatically using a Playwright script, with a visible browser so the user can watch it work.
5. Shows a result per invoice: success or failed, with the reason.

### THE PORTAL WE AUTOMATE (already exists, do not rebuild it)

URL: https://invoice-entry-demo.vercel.app/

- Page "New invoice" has a form. Page "Saved invoices" lists saved records.
- Dates use a date picker. Amounts are plain whole numbers in IDR.
- Line items: 5 rows available. A row must be completely filled or completely empty.
- Buttons: "Save invoice" and "Clear form".

### FIELDS (the PRD must include this as a data table)

Header fields, one value per invoice (form field | label in the PDF):

- invoice_number | Nomor Faktur
- po_number | Nomor PO
- invoice_date | Tanggal Faktur (DD/MM/YYYY in PDF)
- due_date | Jatuh Tempo (DD/MM/YYYY in PDF)
- payment_terms | Syarat Pembayaran
- vendor_name | company name at the top of the document
- vendor_tax_id | NPWP
- vendor_address | address under the vendor name
- bill_to_name | Ditagihkan kepada
- bank | Informasi Pembayaran, "Bank:"
- account_number | No. Rekening

Line items, repeating rows (3 to 5 per invoice): description, quantity (integer), unit, unit_price (IDR integer), line_total (IDR integer)

Totals: subtotal, vat_amount (PPN 11%), total (Total Tagihan)

### DATA RULES (include in the PRD)

- PDF amounts look like "Rp 1.040.000". Store as the plain integer 1040000 (remove "Rp" and the dots).
- PDF dates are DD/MM/YYYY. The portal date picker needs YYYY-MM-DD, so convert before entering.
- The PDF labels are in Indonesian. The portal labels are in English.
- If the vendor address spans several lines in the PDF, join the lines into one text with a comma and a space between them, for example "Jl. Contoh No. 1, Kota 12345".

### BEHAVIOR RULES (include in the PRD)

- Each invoice has one status: Ready, Needs review, Sent, or Failed.
- Extraction sets Needs review if a field is missing or the numbers do not add up (line totals vs subtotal, quantity x unit price vs line total, subtotal + VAT vs total).
- An invoice marked Needs review cannot be sent until the user ticks "I checked this invoice".
- The portal step runs separately from the web app, so a browser problem cannot crash the app.
- An invoice counts as Sent only if the portal's "Saved invoices" count goes up by exactly 1.
- One failed invoice must not stop the others.

### INPUT FILES AVAILABLE IN THE PROJECT FOLDER

- samples/ : 5 demo invoice PDFs. Used in all phases.
- error-samples/ : error sample PDFs. Used only in Phase 3. These files are never edited.

### REQUIRED PHASES (use exactly these 4 phases, in this order)

**Phase 1: Design the UI.** Build only the Streamlit screens with fake placeholder data. No extraction and no automation yet. Screens: upload area, review table with editable fields and a status column, "Send to portal" button, results area.

**Phase 2: Build the automation.**

- a) Set up the project (Python virtual environment, install streamlit, playwright, pdfplumber, run "playwright install chromium").
- b) Build the extraction function: PDF in, structured data out.
- c) Inspect the live portal with Playwright to find the real form fields, labels, and buttons. The PRD must state that the Playwright script is built from this inspection of the live portal, not from guessed selectors.
- d) Turn what you found into a reusable function that takes one invoice's data and fills the portal, including the data conversions above, in a visible browser with a small delay.
- e) Connect extraction and portal filling to the Streamlit buttons.

**Phase 3: Fix and improve.**

- a) Run the error sample PDFs in error-samples/ through the app and find what goes wrong. The known case: a line item row with no unit is skipped, so the line totals no longer add up.
- b) Fix it with general parsing rules, never values copied from a sample. A row without a unit is still extracted with the placeholder "unit", with a warning, and the invoice becomes Needs review. No line item or field may be skipped silently: anything missing or unreadable produces a plain-English warning.
- c) After every fix, all 5 samples in samples/ must still be Ready and still send successfully.
- d) Record every problem and fix in DEBUG_LOG.md.

**Phase 4: Upload to GitHub.** Add README.md (what it does and how to run it), requirements.txt, and .gitignore. HUMAN STEP: I create the empty repository on github.com. Then commit and push. No secrets or personal files in the repository.

For EACH phase, the PRD must contain:

- Goal (one sentence)
- Deliverables (file names)
- "Done when" checklist (3 to 6 yes/no checks a non-programmer can verify by looking at the screen)
- Which steps are done by the AI agent and which are done by me (the human)

### PRD STRUCTURE (use these headings in this order)

1. Problem and goal
2. Users
3. Scope: must have (v1), later, and out of scope
4. User flow (numbered steps, as seen by the user)
5. Functional requirements (numbered, testable)
6. Data specification (field table and data rules)
7. Tech stack and constraints (Python, Streamlit, Playwright, pdfplumber; runs locally; no database; no login; no LLM API)
8. Phases (the 4 phases above)
9. Success metrics (use the BUSINESS FACTS, plus for example: 5 of 5 invoices fully correct)
10. Risks and assumptions

### LATER (list these under "Later" in section 3, as ideas for after v1, not built now)

Support for other vendors' layouts, scanned PDFs with OCR, exporting results to a file. Do not add other Later items.

### OUT OF SCOPE (put these in the PRD as out of scope)

Deployment or hosting, user accounts, a database, scanned or image PDFs, OCR, invoices from other vendors' layouts beyond the 5 samples, editing or deleting saved invoices in the portal, any AI/LLM-based extraction.

When finished, reply with a 5-line summary of the PRD and nothing else.
```

## Prompt 2: Generate UI, Phase 1

Copy the whole box below.

```text
Read PRD.md in this folder. Implement Phase 1 ONLY: Design the UI.

### RULES

- Build only the UI. No PDF extraction, no Playwright, no browser automation, no file saving. Those are Phase 2.
- Everything the UI shows comes from fake placeholder data. Buttons may only simulate results.
- Do not change PRD.md. Do not add features that are not listed below.
- Do not ask me questions. If something is unclear, choose the simplest option and mention it in your final reply.
- Keep the code simple and well commented, because a non-programmer will read it. Use only the Python standard library plus Streamlit.
- Setup: if there is no virtual environment yet, create one in a folder named .venv and install ONLY streamlit. The other packages (playwright, pdfplumber) are installed in Phase 2, not now.
- Keep the invoices and the user's edits in Streamlit session state, so edits survive page reruns and switching between invoices. Phase 2 sends the edited values.

### FILES TO CREATE

- app.py : the Streamlit UI only.
- mock_data.py : one function get_invoices() that returns a list of 3 fake invoices. Each invoice is a dictionary using exactly the field names from the PRD data table (invoice_number, po_number, invoice_date, due_date, payment_terms, vendor_name, vendor_tax_id, vendor_address, bill_to_name, bank, account_number, items, subtotal, vat_amount, total). "items" is a list of dictionaries with description, quantity, unit, unit_price, line_total. Use realistic Indonesian vendor names and values, in the same style as the PRD examples (dates as DD/MM/YYYY, amounts as plain integers). Add a "file" key with a fake PDF file name and a "status" key. This is the structure Phase 2 will replace with real extracted data, so do not rename the fields.

### UI LAYOUT (one page, four numbered sections from top to bottom)

Top: title "Invoice Auto-Entry" and a short subtitle. Show a visible banner: "Phase 1: design preview. All data below is fake."

**Section 1: Upload**

- A file uploader that accepts multiple PDF files.
- A button "Load demo data" next to it, for use when no PDFs are uploaded.
- When files are uploaded OR the button is clicked, load get_invoices() and show sections 2 to 4. Before that, show a friendly empty-state message instead of the empty sections.

**Section 2: Review extracted data**

- A summary table, one row per invoice: file name, invoice number, vendor name, total, status.
- Status values and their look: Ready (green), Needs review (yellow), Sent (blue), Failed (red). Make the first fake invoice Ready, the second Needs review, and the third Ready.
- A selector to choose which invoice to review. Below it, show that invoice as an editable form:
  - Header fields in two columns, grouped under small headings: Invoice details, Vendor, Bill to, Payment.
  - Line items in an editable table with columns: Description, Qty, Unit, Unit price (IDR), Line total (IDR).
  - Totals: Subtotal, VAT amount (PPN 11%), Total.
- Show amounts with Indonesian thousand separators (Rp 1.040.000) for display. Keep the underlying value a plain integer. If Streamlit cannot format the separators inside an editable table cell, show the formatted amount as read-only text next to the editable plain number.
- For the invoice with status "Needs review", highlight one field with a short warning message such as "Please check this value".

**Section 3: Send to portal**

- Button "Send selected invoice to portal" and button "Send all invoices to portal".
- When clicked, simulate the work: show a progress bar and a spinner for about 2 seconds, then set the status to Sent. Show the text "Demo only. Real automation is built in Phase 2." near the buttons.

**Section 4: Results**

- A results table with columns: file name, status, message. Show messages like "Saved to portal" or "Failed: field not found".
- Make the second invoice end as Failed when "Send all" is clicked, so the failed state is visible. Add a "Retry failed" button that turns it into Sent.

### STYLE

- Clean and professional. Use Streamlit columns, containers, and expanders. Wide layout. No custom HTML or CSS unless essential.
- Use plain business English in all labels. No technical jargon on the screen.

### BEFORE YOU FINISH

Confirm the app starts without errors by running it headless (streamlit run app.py --server.headless true) or by using Streamlit's AppTest, then make sure no Streamlit process is left running. Check each item below yourself:

1. "streamlit run app.py" opens without errors.
2. The empty state shows before any data is loaded.
3. After "Load demo data", all four sections appear.
4. All four status colors can be seen at some point.
5. Editing a field in the review form works and does not crash.
6. "Send all" simulates progress and ends with one Failed row, and "Retry failed" fixes it.
7. No PDF reading and no browser automation exists anywhere in the code.

### FINAL REPLY

Tell me, in at most 6 lines: the exact command to run the app, what I should click to see each section, and any assumption you made.
```

## Prompt 3: Build the Automation, Phase 2

Copy the whole box below.

```text
Read PRD.md and the existing files in this folder (app.py, mock_data.py). Implement Phase 2: build the automation. This has two parts and needs no human step.

### GLOBAL RULES

- No AI or LLM API calls. Extraction uses pdfplumber and plain Python parsing rules only.
- Do not rename fields. Extraction output must use exactly the same dictionary structure as mock_data.py so the UI keeps working.
- Do not ask me questions. If something is unclear, choose the simplest option and mention it in your replies.
- Keep code simple and commented for a non-programmer.

### PART A: SETUP AND EXTRACTION

**A1. Setup**

- Use the existing .venv. Install streamlit, playwright, and pdfplumber. Run "playwright install chromium".
- Create requirements.txt with the three packages. Confirm all three import without errors.

**A2. Study the PDFs first**

- Extract and print the raw text of ALL 5 PDFs in samples/. Read them carefully. The vendors have slightly different layouts and invoice number formats, so write parsing rules from the actual text, not from assumptions.

**A3. Build extract.py**

- Main function parse_invoice(pdf_path) returns a dictionary with keys: file, invoice_number, po_number, invoice_date, due_date, payment_terms, vendor_name, vendor_tax_id, vendor_address, bill_to_name, bank, account_number, items, subtotal, vat_amount, total, status, warnings.
- items is a list of dictionaries with: description, quantity, unit, unit_price, line_total.
- Data rules:
  - Dates stay as text in DD/MM/YYYY exactly as in the PDF. Conversion happens later in the portal step.
  - Amounts and quantities become plain integers. "Rp 1.040.000" becomes 1040000.
  - vendor_name is the company name at the top of the document. vendor_address is the address under it. If the address spans several lines in the PDF, join the lines with a comma and a space, for example "Jl. Contoh No. 1, Kota 12345". Do not add a second comma if a line already ends with one.
  - Find values using the Indonesian labels (Nomor Faktur, Nomor PO, Tanggal Faktur, Jatuh Tempo, Syarat Pembayaran, NPWP, Ditagihkan kepada, Bank, No. Rekening, Subtotal, PPN 11%, Total Tagihan).
  - Do not extract fields that are not in the portal form (for example phone number or bill-to address).
- Validation inside parse_invoice:
  - For any missing or empty field, add a plain-English message to "warnings" (example: "Could not find Due date").
  - Check that line totals add up to subtotal, that quantity x unit price equals line total for each row, and that subtotal + vat_amount equals total. Add a warning for each mismatch.
  - status is "Ready" if there are no warnings, otherwise "Needs review". Put these checks in their own function, validate_invoice(invoice), that works on a dictionary and never reads a PDF. The app calls it again after the user edits values.
- Never crash on a bad PDF. Return an invoice with status "Needs review" and a warning that explains the problem.

**A4. Build try_extract.py**

- Runs parse_invoice on every PDF in samples/ and prints a readable summary per invoice. This is a visual sanity check only.

**A5. Connect extraction to the UI (app.py)**

- Uploaded PDFs: save to a temporary folder, run parse_invoice on each, show results in the existing sections 2 to 4.
- Replace "Load demo data" with "Load sample invoices", which runs the same extraction on the PDFs in samples/.
- Remove the "Phase 1: design preview. All data below is fake." banner.
- Show each invoice's warnings next to the related field when possible, otherwise as a list above the form.
- Keep the Send buttons simulated for now with the text "Portal automation is added in the next step."
- Remove the forced-failure logic from Phase 1. Keep mock_data.py but do not use it.

**A6. Verify Part A**

- Run try_extract.py. Every sample must show 3 to 5 line items and plausible values. Fix your parsing rules if not.
- Start the app once to confirm it runs without errors, then stop it.

### PART B: PORTAL AUTOMATION (start after Part A is verified)

Inspect the live portal first, then build the automation from what you find. Do not guess selectors.

**B1. Build portal.py**

- Find the selectors by inspecting the live portal: open https://invoice-entry-demo.vercel.app/ with a short throwaway Playwright script and list every form field, label, input type, and button, plus the "Saved invoices" link in the top navigation. Prefer selectors based on labels and roles (get_by_label, get_by_role) over fragile CSS paths. Do not guess selectors. If you cannot reach the portal, tell me and stop. Delete the throwaway script when you are done.
- Function fill_invoice(page, invoice): opens https://invoice-entry-demo.vercel.app/, fills the form from ONE invoice dictionary, clicks "Save invoice". Before clicking Save, read back every field and compare it with the value you typed. If any field differs, do not click Save and return Failed with the field name. No hardcoded invoice values anywhere. Every form value must come from the invoice dictionary.
- Data conversions before typing:
  - Dates: DD/MM/YYYY to YYYY-MM-DD. For date fields always use fill() with the YYYY-MM-DD text, not mouse clicks on the date picker.
  - Amounts and quantities: plain integers typed as text, no dots, no "Rp".
- Line items: fill only as many rows as the invoice has, starting at row 1, and leave the other rows completely empty. The portal rejects half-filled rows. If an invoice has more than 5 items, do not enter it and return Failed with the message "More than 5 line items, portal supports 5".
- Success check: read the "Saved invoices" count in the top navigation before clicking Save and again after. Success means it increased by exactly 1. If the portal shows a clearer confirmation message after saving, check that too. Otherwise return Failed with a clear reason.
- Wrap each invoice in try/except. One failed invoice must NOT stop the others. On failure, save a screenshot into screenshots/ and include the file name in the message.
- Function send_invoices(invoices): opens ONE visible browser (headless=False, slow_mo=300) with ONE browser context, processes all invoices in order (finishing on the Saved invoices page and pausing 5 seconds so I can see the result), closes the browser, and returns a list of {file, status ("Sent" or "Failed"), message}.

**B2. Run Playwright as a separate process**

- Streamlit and Playwright can conflict, especially on Windows. Make portal.py runnable from the command line: "python portal.py --input in.json --output out.json". It reads a list of invoices from the input file, runs send_invoices, and writes the results to the output file.
- In app.py, call it with subprocess.run([sys.executable, "portal.py", ...]) using temporary JSON files and a spinner. Never run Playwright inside the Streamlit process.

**B3. Connect to the UI (app.py)**

- "Send selected invoice to portal" sends only the selected invoice, using the VALUES CURRENTLY IN THE EDITABLE FORM, including my corrections.
- "Send all invoices to portal" sends all invoices using the current edited values.
- "Retry failed" sends only invoices whose status is Failed.
- After a run, update each invoice's status to Sent or Failed and fill the Results table with the real file name, status, and message.
- Block sending, with a clear message, for any invoice with status "Needs review" until I tick a checkbox "I checked this invoice" for that invoice. Run validate_invoice on the edited values first, so the status reflects my corrections.
- Remove the text "Portal automation is added in the next step."

**B4. Verify Part B**

- Test against the real portal in a visible browser: send invoice 1 first, then all 5. If your environment cannot open a browser window, do not fake it. Tell me, and give me the exact commands to test myself.
- Check: (1) a visible browser fills the portal without my help, (2) the Saved invoices count goes up by one per sent invoice, (3) a corrected value in the review form is the value typed into the portal, (4) an invoice with an empty vendor name fails without stopping the rest, (5) no invoice value is hardcoded in portal.py.

### FINAL REPLY (at most 6 lines)

The command to run the app, which of the 5 invoices were sent successfully, and any assumption you made.
```

## Prompt 4: Fix and Improve, Phase 3

Human step first: run the app, upload error-samples/error_01_karya_solusi.pdf, and look at the review screen. Line 2 is missing and the totals do not add up. Then copy the whole box below.

```text
Read PRD.md and the existing project files (app.py, extract.py, portal.py). I tested the invoice error-samples/error_01_karya_solusi.pdf and found a problem. Fix it.

**THE PROBLEM**

Line 2 of this invoice has no value in the Satuan (unit) column. The parser does not find that line, so it is left out of the extracted items, and the line totals no longer add up to the subtotal. The portal also rejects a line row that is only partly filled.

**THE FIX**

- A line item row with no unit must still be extracted. Use the placeholder "unit" as its unit, so the row is fully filled in the portal. Apply this to any row without a unit, not only this file.
- When the placeholder is used, add a warning in plain English, for example: "Line 2 has no unit. The placeholder 'unit' was used." The invoice status then becomes Needs review, so the user sees the change.
- No other line item may ever be skipped silently. If a row cannot be read at all, add a warning instead.

**RULES**

- Never edit, rename, or delete any file in samples/ or error-samples/. Change only the app code.
- Do NOT hardcode any value from the sample or error sample invoices (names, numbers, file names) into extract.py or portal.py. A fix is only valid if it works by reading the PDF text with general rules.
- A fix must not break the others. After every fix, all 5 sample invoices must still be Ready and still send successfully.
- A clear warning in plain English is a valid fix if the data cannot be read safely. An invoice marked Ready with wrong values, or saved to the portal with wrong values, is never acceptable.
- Do not change the screen layout. You may add or reword warning and error messages.
- No AI or LLM API calls. Use only the packages the project already uses.
- Do not claim something is fixed unless you reran it and saw the result. Show the real output.
- Do not ask me questions. If something is unclear, choose the simplest option and mention it in your final reply.
- Keep code simple and commented for a non-programmer.

**TASK**

1. Read the raw text of the error sample PDF and the line item parsing rule in extract.py. Confirm the cause in plain words, 3 lines at most.
2. Make the smallest general fix in extract.py or portal.py.
3. Rerun the error sample and show the real output. It must have 3 line items, line 2 must have the placeholder unit and a warning, and the line totals must add up to the subtotal. Then rerun all 5 samples and show the real output.
4. If a sample stopped working, undo the fix and try a different one.
5. Then check how the parser handles any other missing or unreadable value in a line item row (description, quantity, unit price, line total) and in the header fields. Nothing may be skipped silently: each one must produce a clear warning that says what happened and what to check next, in plain business English, and the invoice must show Needs review. Fix any gap with a general rule in extract.py. Rerun the error sample and all 5 samples again.
6. Maximum 3 attempts per fix. If it still fails, stop and report exactly what still fails and why. Do not hack around it.
7. Add entries to DEBUG_LOG.md (create it if missing): invoice, what went wrong, cause, fix, result.

**FINAL REPLY (at most 4 lines)**

The cause, what you changed (including any extra checks you added), and the result for the error sample and for the 5 samples.
```

## Prompt 5: Upload to GitHub, Phase 4

Copy the whole box below. The AI will stop and ask for your GitHub repository URL. Do the steps it lists, then paste the URL as your next message. If it asks you to set your git name or email, or to sign in, do that in your own terminal and then type "continue".

```text
Read PRD.md and the existing project files. Upload this project to GitHub. There is ONE required stop in the middle, because I have to create the empty repository myself.

**RULES**

- Never use force push. Never delete files or rewrite git history.
- Never ask me for a password or token. If sign-in is needed, tell me to run the command in my own terminal.
- Do not change the app code. The only files you create or edit are README.md, .gitignore, requirements.txt, and git itself.
- Do not set global git settings. Use repository-local settings only.
- Do not say something was pushed unless you verified it with the commands below. Show the real output.
- Do not ask me questions. If something is unclear, choose the simplest option and mention it in your final reply.

**PART A: PREPARE**

1. Check that git is installed. If not, tell me to install it from https://git-scm.com/downloads, then stop until I type "continue". If this folder is not a git repository yet, run "git init -b main".
2. Create .gitignore. It must exclude: `.venv/`, `__pycache__/`, `*.pyc`, `screenshots/`, `.DS_Store`, `Thumbs.db`, and the temporary files the app creates (check app.py and portal.py for their names).
3. Create or update requirements.txt with the exact installed versions of streamlit, playwright, and pdfplumber (format: package==version).
4. Create README.md in plain English, maximum 1 page, with: what the tool does (one sentence and 3 to 5 bullets), a note that all data is fictional and the portal is a demo site, setup (create and activate the virtual environment for Mac/Linux and Windows, pip install -r requirements.txt, playwright install chromium), how to run (the exact app command and what to click), and the project structure (one line per file or folder). Only describe features that exist.

**REQUIRED STOP: HUMAN STEP**

After Part A, stop. Reply with exactly this:

"PART A DONE. NOW IT IS YOUR TURN:"

"1. Go to https://github.com/new and sign in."

"2. Repository name: invoice-auto-entry. Choose Private. Do NOT tick Add a README, Add .gitignore, or Choose a license. Click Create repository."

"3. Copy the repository URL (it ends with .git)."

"4. Come back here and paste the URL."

[Only if git user.name or user.email is not set, also add: "Before pasting the URL, run these two commands in your terminal with your own details: git config user.name "Your Name" and git config user.email "you@example.com". If you use your GitHub noreply email, find it at https://github.com/settings/emails."]

**PART B: PUSH (only after I paste the URL)**

1. If there is no commit yet, run "git add -A" and commit with the message "Initial commit: invoice auto-entry tool".
2. Run "git remote add origin <URL>" (if origin already exists, use "git remote set-url origin <URL>"), then "git push -u origin main".
3. If the push asks for sign-in or fails because of authentication, do not retry and do not ask for credentials. Tell me to run "git push -u origin main" in my own terminal in the project folder and sign in through the browser window GitHub opens, then type "continue". If the push is rejected because the repository is not empty, tell me to create a new empty repository. Never force push.
4. Verify: run "git status", "git log --oneline", and "git ls-remote origin". The remote main must show the same commit as my local one. Show the real output.

**FINAL REPLY (at most 3 lines)**

The repository URL, and whether the push is verified (yes or no).
```
