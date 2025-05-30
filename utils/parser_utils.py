import re
import cv2
import numpy as np
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def parse_invoice_data(text_blocks):
    text = " ".join([block["text"] for block in text_blocks])
    text = text.replace("\n", " ").replace(":", " : ").replace("  ", " ")

    def extract(pattern):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def clean_address(addr):
        addr = re.sub(r"(Phone\s*\d{10})", "", addr)
        addr = re.sub(r"\b(\w+\s*)\1{1,}", r"\1", addr)
        addr = re.sub(r"\s+", " ", addr)
        return addr.strip(", ;:- ")

    gstins = re.findall(r"(?:GSTIN|GSTIN\s*No|GST\s*Number)[\s:\-]*([0-9A-Z]{13,17})", text, flags=re.IGNORECASE)
    gstins = [g[:15] for g in gstins]

    return {
        "invoice_number": extract(r"(?:Invoice\s*No|Invoice\s*#|Inv\s*No)[\.\:\-]?\s*([A-Za-z0-9\-\/]+)"),
        "invoice_date": extract(r"(?:Invoice\s*Date|Date)[\.\:\-]?\s*([\d]{2}[\/\-][\d]{2}[\/\-][\d]{4})"),
        "supplier_gst_number": gstins[0] if len(gstins) > 0 else "",
        "bill_to_gst_number": gstins[1] if len(gstins) > 1 else "",
        "po_number": extract(r"(?:PO\s*Number|P\.O\. No|Purchase Order)\s*[:\-]?\s*([\w\-\/]+)"),
        "shipping_address": clean_address(extract(r"(?:Ship\s*To|Shipping Address)\s*[:\-]?\s*(.*?)(?:GSTIN|GST|Phone|PO|Invoice)"))
    }

def extract_table_data(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    grid_mask = cv2.add(horizontal_lines, vertical_lines)

    contours, _ = cv2.findContours(grid_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cells = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 40 < w < 800 and 20 < h < 200:
            cells.append((x, y, w, h))
    cells = sorted(cells, key=lambda b: (b[1], b[0]))

    rows, current_row, last_y = [], [], -1
    for box in cells:
        x, y, w, h = box
        if last_y == -1 or abs(y - last_y) <= 15:
            current_row.append(box)
            last_y = y
        else:
            rows.append(sorted(current_row, key=lambda b: b[0]))
            current_row = [box]
            last_y = y
    if current_row:
        rows.append(sorted(current_row, key=lambda b: b[0]))

    extracted_table = []
    for row in rows[1:]:
        row_data = []
        for (x, y, w, h) in row:
            cell_img = img[y:y+h, x:x+w]
            result = reader.readtext(cell_img, detail=0)
            cell_text = result[0].strip() if result else ""
            row_data.append(cell_text)
        if len(row_data) >= 6:
            extracted_table.append({
                "serial_number": row_data[0],
                "description": row_data[1],
                "hsn_sac": row_data[2],
                "quantity": row_data[3],
                "unit_price": row_data[4],
                "total_amount": row_data[5]
            })
        else:
            extracted_table.append({f"col_{i}": val for i, val in enumerate(row_data)})
    return extracted_table
