"""
Fake invoice data for the Phase 1 design preview.

In Phase 2 this file is replaced by real data read from the PDF files.
The field names below match the data table in PRD.md, so do not rename them.

Rules used here (same as the PRD):
- Dates are text in the form DD/MM/YYYY.
- Amounts are plain whole numbers in Indonesian Rupiah (no "Rp", no dots).
"""


def get_invoices():
    """Return a list of 3 fake invoices (one dictionary per invoice)."""
    return [
        # ---------------------------------------------------------------
        # Invoice 1: all values add up, so its status is "Ready".
        # ---------------------------------------------------------------
        {
            "file": "invoice_sinar_kertas.pdf",
            "status": "Ready",
            "invoice_number": "INV/SKA/2026/03/0142",
            "po_number": "PO-2026-0311",
            "invoice_date": "05/03/2026",
            "due_date": "04/04/2026",
            "payment_terms": "Net 30",
            "vendor_name": "PT Sinar Kertas Abadi",
            "vendor_tax_id": "01.234.567.8-012.000",
            "vendor_address": "Jl. Mangga Dua Raya No. 18, Jakarta Utara 14430",
            "bill_to_name": "PT Nusantara Makmur Sejahtera",
            "bank": "Bank Central Asia (BCA)",
            "account_number": "5270123456",
            "items": [
                {"description": "Kertas HVS A4 80gsm", "quantity": 20, "unit": "rim",
                 "unit_price": 52000, "line_total": 1040000},
                {"description": "Tinta Printer Epson 664 Hitam", "quantity": 10, "unit": "botol",
                 "unit_price": 85000, "line_total": 850000},
                {"description": "Map Plastik Snelhecter", "quantity": 50, "unit": "pcs",
                 "unit_price": 3500, "line_total": 175000},
            ],
            "subtotal": 2065000,
            "vat_amount": 227150,
            "total": 2292150,
        },
        # ---------------------------------------------------------------
        # Invoice 2: the total is wrong on purpose (subtotal + VAT is
        # 5244750, but the total says 5247750), so it is "Needs review".
        # ---------------------------------------------------------------
        {
            "file": "invoice_mitra_teknologi.pdf",
            "status": "Needs review",
            "invoice_number": "MTI-0326-0087",
            "po_number": "PO-2026-0318",
            "invoice_date": "10/03/2026",
            "due_date": "24/03/2026",
            "payment_terms": "Net 14",
            "vendor_name": "CV Mitra Teknologi Indonesia",
            "vendor_tax_id": "02.876.543.2-421.000",
            "vendor_address": "Jl. Asia Afrika No. 112, Bandung 40261",
            "bill_to_name": "PT Nusantara Makmur Sejahtera",
            "bank": "Bank Mandiri",
            "account_number": "1300098765432",
            "items": [
                {"description": "Mouse Wireless Logitech M170", "quantity": 10, "unit": "unit",
                 "unit_price": 125000, "line_total": 1250000},
                {"description": "Keyboard USB Standar", "quantity": 10, "unit": "unit",
                 "unit_price": 150000, "line_total": 1500000},
                {"description": "Kabel HDMI 2 meter", "quantity": 15, "unit": "pcs",
                 "unit_price": 45000, "line_total": 675000},
                {"description": "Flashdisk 32GB", "quantity": 20, "unit": "pcs",
                 "unit_price": 65000, "line_total": 1300000},
            ],
            "subtotal": 4725000,
            "vat_amount": 519750,
            "total": 5247750,
        },
        # ---------------------------------------------------------------
        # Invoice 3: all values add up, so its status is "Ready".
        # ---------------------------------------------------------------
        {
            "file": "invoice_boga_rasa.pdf",
            "status": "Ready",
            "invoice_number": "BR/FKT/2026/0215",
            "po_number": "PO-2026-0322",
            "invoice_date": "12/03/2026",
            "due_date": "11/04/2026",
            "payment_terms": "Net 30",
            "vendor_name": "PT Boga Rasa Nusantara",
            "vendor_tax_id": "03.112.334.5-603.000",
            "vendor_address": "Jl. Raya Darmo No. 45, Surabaya 60265",
            "bill_to_name": "PT Nusantara Makmur Sejahtera",
            "bank": "Bank Rakyat Indonesia (BRI)",
            "account_number": "0123-01-004567-50-3",
            "items": [
                {"description": "Nasi Kotak Rapat", "quantity": 50, "unit": "kotak",
                 "unit_price": 35000, "line_total": 1750000},
                {"description": "Snack Box", "quantity": 50, "unit": "kotak",
                 "unit_price": 15000, "line_total": 750000},
                {"description": "Air Mineral 600ml", "quantity": 4, "unit": "dus",
                 "unit_price": 48000, "line_total": 192000},
            ],
            "subtotal": 2692000,
            "vat_amount": 296120,
            "total": 2988120,
        },
    ]
