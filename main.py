import os
import json
import pandas as pd
import numpy as np
import re
from PIL import Image
from utils.ocr_utils import pdf_to_images, extract_text_with_boxes
from utils.parser_utils import parse_invoice_data, extract_table_data
from utils.verify_utils import verify_and_score

input_dir = "input/"
output_dir = "output/"
os.makedirs(output_dir, exist_ok=True)

all_data = []
verifiability = []

def try_float(value):
    try:
        val = str(value)
        val = re.sub(r"[^\d.]", "", val)
        parts = val.split(".")
        if len(parts) > 2:
            val = parts[0] + "." + "".join(parts[1:])
        return float(val)
    except:
        return None

def convert_numpy(obj):
    if isinstance(obj, (np.integer, np.int_)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float_)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return str(obj)

def is_valid_item(row):
    if any(k.startswith("col_") for k in row.keys()):
        return False
    fields = ["description", "hsn_sac", "quantity", "unit_price", "total_amount"]
    non_empty = sum(1 for f in fields if row.get(f, "").strip() not in ["", "DESCRIPTION", "HSN NO_", "QTY", "RATE", "AMOUNT"])
    return non_empty >= 3

def clean_items(items):
    cleaned = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        if any(isinstance(v, str) and v.strip() for v in item.values()):
            if is_valid_item(item):
                item["serial_number"] = str(i + 1)
                item["unit_price"] = str(try_float(item.get("unit_price", "")) or "")
                item["total_amount"] = str(try_float(item.get("total_amount", "")) or "")
                item["quantity"] = str(try_float(item.get("quantity", "")) or "")
                for k in item:
                    if isinstance(item[k], str):
                        item[k] = item[k].strip()
                cleaned.append(item)
    return cleaned

def extract_financials_from_text(text_blocks):
    text = " ".join([block["text"] for block in text_blocks]).replace(",", "")
    
    def extract_value(pattern):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return try_float(match.group(1))
        return None

    discount = extract_value(r"Discount\s*[:\-]?\s*\₹?\s*([\d.]+)")
    gst_values = re.findall(r"(?:CGST|SGST|IGST)[^\d]*([\d.]+)", text, flags=re.IGNORECASE)
    gst_total = sum([try_float(g) for g in gst_values if try_float(g)])
    final_total = extract_value(r"(?:Total Amount|Grand Total|Payable Amount)\s*[:\-]?\s*\₹?\s*([\d.]+)")

    return {
        "discount": discount or 0.0,
        "gst": gst_total or 0.0,
        "final_total": final_total or 0.0
    }

for idx, file in enumerate(os.listdir(input_dir)):
    if file.endswith(".pdf"):
        print(f"\n[{idx+1}] Processing: {file}")
        images = pdf_to_images(os.path.join(input_dir, file))
        all_text = []
        all_items = []

        for i, img in enumerate(images):
            text_data = extract_text_with_boxes(img)
            all_text.extend(text_data)
            if i == len(images) - 1:
                items = extract_table_data(img)
                all_items = clean_items(items)

        invoice_data = parse_invoice_data(all_text)
        invoice_data["items"] = all_items

        financials = extract_financials_from_text(all_text)
        invoice_data["discount"] = financials["discount"]
        invoice_data["gst"] = financials["gst"]
        invoice_data["final_total"] = financials["final_total"]

        subtotal = sum(try_float(item.get("total_amount", "")) or 0 for item in all_items)
        invoice_data["subtotal"] = round(subtotal, 2)

        report, cropped_img = verify_and_score(images[-1], invoice_data, text_blocks=all_text)
        invoice_data["seal_and_sign_present"] = report["seal_and_sign_present"]

        all_data.append(invoice_data)
        verifiability.append(report)

        if cropped_img is not None:
            cropped_img.save(os.path.join(output_dir, f"seal_signature_{idx+1}.png"))

        if all_items:
            pd.DataFrame(all_items).to_csv(os.path.join(output_dir, f"invoice_items_{idx+1}.csv"), index=False)

with open(os.path.join(output_dir, "extracted_data.json"), "w") as f:
    json.dump(all_data, f, indent=4, default=convert_numpy)

summary_data = [{**entry, "num_items": len(entry.get("items", []))} for entry in all_data]
pd.DataFrame(summary_data).to_excel(os.path.join(output_dir, "extracted_data.xlsx"), index=False)

with open(os.path.join(output_dir, "verifiability_report.json"), "w") as f:
    json.dump(verifiability, f, indent=4, default=convert_numpy)

print("\n Extraction complete. Outputs saved in 'output/' folder.")
