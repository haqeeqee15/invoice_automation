# Debug log

## 2026-11-11 — error-samples/error_01_karya_solusi.pdf: line item with no unit

- **What went wrong:** Line 2 ("Konfigurasi dan pelatihan staf 2 Rp 1.250.000 Rp 2.500.000") has no value in the Satuan column. It was left out of the line items, so the line totals no longer added up to the subtotal, and the portal refused a partly filled row.
- **Cause:** The line item rule expected a unit word between the quantity and the first "Rp". A row with no unit did not match the rule, so it was dropped.
- **Fix (extract.py):** The unit is optional in the row rule. A row with no unit gets the placeholder "unit" and the warning "Line N has no unit. The placeholder 'unit' was used. Please check the unit in the PDF." The invoice becomes Needs review. This rule works for any row.
- **Result (rerun):** 3 line items. Line 2 has unit "unit" and the warning. Line totals 9,450,000 = Subtotal 9,450,000. Status: Needs review. Sent to the portal as REC-0006. All 5 samples are still Ready and Sent (REC-0001 to REC-0005).

## 2026-11-11 — General check: other missing or unreadable values (tested on in-memory copies of the PDF text, no sample file changed)

- **What went wrong:**
  1. A row missing its description, quantity, unit price or line total was dropped with only a generic "Could not read this row" message. The review table has a fixed number of rows, so the user could not add the row back.
  2. Amounts with a decimal comma (for example "Rp 212.300,50") were read as a different whole number (21230050) with no warning.
  3. A date not written as DD/MM/YYYY was marked Ready, and only failed later in the portal.
  4. Warnings did not say what to check next.
  5. If the "Subtotal" line was missing, the PPN, Total and bank lines were treated as broken line item rows.
  6. portal.py could type an empty description or unit into the portal.
- **Cause:** The parser only knew a perfect row, and amounts were read by keeping every digit.
- **Fix:**
  - extract.py: amounts are accepted only as "Rp" plus groups of 3 digits split by dots. Anything else is left empty with a warning.
  - extract.py: a numbered row that does not fully match is still kept. Only the cells that can be read safely are filled in. The rest stay empty, with a warning that names the empty cells. If there is only one amount, both amount cells stay empty, because we cannot tell which one it is.
  - extract.py: a row with no row number is reported with its text.
  - extract.py: dates are checked as DD/MM/YYYY.
  - extract.py: the table ends at the first totals line.
  - extract.py: every warning now says what to check next.
  - portal.py: an empty description or unit stops the send before anything is typed.
  - app.py: uses the new missing-field wording, so the warnings stay in the same place on screen.
- **Result (rerun):** All 13 test cases show Needs review with a clear warning: no description, no quantity, no unit price, no line total, comma amount, decimal quantity, unnumbered row, missing PO, empty bank, bad date, bad VAT, missing Subtotal, missing table heading. The error sample still has 3 items and the placeholder warning. All 5 samples are still Ready and were Sent.
