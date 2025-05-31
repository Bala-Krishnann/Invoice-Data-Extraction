# Invoice Data Extraction 📄🔍

This project automates the extraction of structured information from scanned invoice PDFs or images. It utilizes OCR and rule-based parsing to retrieve key invoice fields and outputs the data in structured formats for downstream use.

## 🚀 Features

- 📦 Extract general invoice fields:
  - Invoice Number
  - Invoice Date
  - Supplier & Buyer GST Numbers
  - PO Number
  - Shipping Address
- 📋 Extract line-item table:
  - Serial Number
  - Item Description
  - HSN/SAC Code
  - Quantity
  - Unit Price
  - Total Amount
- 🧾 Detect and save Seal/Signature (if present)
- 💾 Outputs structured JSON and Excel files
- 🧠 Designed for scanned (image-based) invoices

## 🗂️ Project Structure

```
Invoice-Data-Extraction/
│
├── input/                   # Folder containing invoice images or PDFs
├── output/                  # Extracted results: JSON, Excel, cropped seals
├── main.py                  # Entry-point script for extraction
├── utils/                   # Helper functions and modules
├── ReadMe.txt               # Initial readme notes
├── requirements.txt         # Required Python packages
└── README.md                # GitHub-friendly README (this file)
```

## ⚙️ Requirements

- Python 3.8+
- OpenCV
- EasyOCR
- Pandas
- NumPy
- Pillow

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

```json
{
  "invoice_number": "INV-12345",
  "invoice_date": "15-03-2023",
  "supplier_gst_number": "27AAAPL1234C1Z9",
  "bill_to_gst_number": "29BBAPM4321F1ZT",
  "shipping_address": "ABC Pvt Ltd, Sector-5, Noida, UP",
  "seal_and_sign_present": true,
  "items": [
    {
      "serial_number": "1",
      "description": "Widget A",
      "hsn_sac": "8471",
      "quantity": "10",
      "unit_price": "50.00",
      "total_amount": "500.00"
    }
  ],
  "discount": 0.0,
  "gst": 18.0,
  "total_amount": 590.0
}
```

## 📌 Future Improvements

- Improve robustness with deep learning-based key-value detection
- Multilingual invoice support
- Invoice layout classification
- Integrate LayoutLM/Donut for better field mapping

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📝 License

This project is licensed under the MIT License.

## 🙌 Acknowledgements

- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [OpenCV](https://opencv.org/)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) (for future extensions)
