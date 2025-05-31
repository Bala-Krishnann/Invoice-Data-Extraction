# Invoice Data Extraction 📄🔍

This project automates the extraction of structured information from scanned invoice PDFs or images. It utilizes OCR and rule-based parsing to retrieve key invoice fields and outputs the data in structured formats for downstream use.

## 🚀 Features

-   📦 Extract general invoice fields:
    -   Invoice Number
    -   Invoice Date
    -   Supplier & Buyer GST Numbers
    -   PO Number
    -   Shipping Address
-   📋 Extract line-item table:
    -   Serial Number
    -   Item Description
    -   HSN/SAC Code
    -   Quantity
    -   Unit Price
    -   Total Amount
-   🧾 Detect and save Seal/Signature (if present)
-   💾 Outputs structured JSON and Excel files
-   🧠 Designed for scanned (image-based) invoices

## 🗂️ Project Structure

```
Invoice-Data-Extraction/
│
├── input/                   # Folder containing invoice images or PDFs
├── output/                  # Extracted results: JSON, Excel, cropped seals
├── main.py                  # Entry-point script for extraction
├── utils/                   # Helper functions and modules
├── requirements.txt         # Required Python packages
└── README.md                # GitHub-friendly README (this file)
```

## ⚙️ Requirements

-   Python 3.8+
-   OpenCV
-   EasyOCR
-   Pandas
-   NumPy
-   Pillow

Install dependencies using:

```bash
pip install -r requirements.txt
```

## 📥 How to Use

1. **Clone this repository**:

    ```bash
    git clone https://github.com/Bala-Krishnann/Invoice-Data-Extraction.git
    cd Invoice-Data-Extraction
    ```

2. **Add your invoices**:
   Place your scanned invoice PDFs or image files (JPG, PNG) into the `input/` directory.

3. **Run the main script**:

    ```bash
    python main.py
    ```

4. **Check the output**:
    - `output/extracted_data.json` – structured invoice data
    - `output/extracted_data.xlsx` – same data in Excel
    - `output/seal_sign.jpg` – cropped image if seal/signature detected
    - `output/verifiability_report.json` – field-wise confidence & validation report

## 📊 Sample Output (JSON)

`````json
"invoice_number": "654654",
        "invoice_date": "15-03-2021",
        "supplier_gst_number": "696969696969696",
        "bill_to_gst_number": "696969696969696",
        "po_number": "",
        "shipping_address": "Nazim Khan Nazim Khan Sector-200,Noida, UP Sector-200,Noida; UP Uttar Pradesh (Uttar Pradesh",
        "items": [
            {
                "serial_number": "2",
                "description": "ITEM NAME 2",
                "hsn_sac": "2541",
                "quantity": "26.0",
                "unit_price": "0.23552",
                "total_amount": "0.612352"
            },
            {
                "serial_number": "4",
                "description": "ITEM NAME 5",
                "hsn_sac": "8151",
                "quantity": "15.0",
                "unit_price": "0.215",
                "total_amount": "0.3225"
            }
        ],
        "discount": 0.0,
        "gst": 15.0,
        "final_total": 0.0,
        "subtotal": 0.93,
        "seal_and_sign_present": {
            "value": false,
            "confidence": 1.0,
            "verified": false
        }````

## 📌 Future Improvements

- Predict the positions of invoice fields (like invoice_number, gst_number, etc.) in unseen invoice images using a trained object detection model.
- Extract text from the predicted field boxes and map them to structured invoice fields.
- Use simple regex and cleaning to sanitize values.

`````
