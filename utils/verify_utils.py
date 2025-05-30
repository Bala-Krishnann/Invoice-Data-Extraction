import cv2
import numpy as np
from PIL import Image
import re

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

def verify_and_score(image, parsed_data, text_blocks=None):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    seal_detected = False
    seal_crop = None
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 50 < w < 300 and 50 < h < 200:
            seal_crop = img[y:y+h, x:x+w]
            seal_detected = True
            break

    report = {}
    low_confidence_fields = []

    for field in ['invoice_number', 'invoice_date', 'supplier_gst_number', 'bill_to_gst_number', 'po_number', 'shipping_address']:
        value = parsed_data.get(field, "")
        confidence = 0.0
        if value and text_blocks:
            for block in text_blocks:
                if value.lower() in block['text'].lower():
                    confidence = max(confidence, block['conf'] / 100.0)
        report[field] = {
            "value": value,
            "confidence": round(confidence, 2),
            "verified": confidence >= 0.6
        }
        if confidence < 0.6:
            low_confidence_fields.append(field)

    item_checks = []
    subtotal = 0.0
    for item in parsed_data.get("items", []):
        unit = try_float(item.get("unit_price", ""))
        qty = try_float(item.get("quantity", ""))
        total = try_float(item.get("total_amount", ""))
        correct = unit is not None and qty is not None and total is not None and abs(unit * qty - total) < 1.0
        item_checks.append({
            "serial_number": item.get("serial_number", ""),
            "unit_price": unit,
            "quantity": qty,
            "total_amount": total,
            "verified": correct
        })
        if correct and total:
            subtotal += total

    discount = try_float(parsed_data.get("discount", 0.0))
    gst_amount = try_float(parsed_data.get("gst", 0.0))
    final_total = subtotal - discount + gst_amount
    parsed_final_total = try_float(parsed_data.get("final_total", 0.0))
    formula_verified = abs(parsed_final_total - final_total) < 1.0 if parsed_final_total else False

    total_checks = {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "gst_amount": round(gst_amount, 2),
        "expected_final_total": round(final_total, 2),
        "parsed_final_total": parsed_final_total,
        "formula_verified": formula_verified
    }

    report["seal_and_sign_present"] = {
        "value": seal_detected,
        "confidence": 1.0,
        "verified": seal_detected
    }
    report["line_items"] = item_checks
    report["total_checks"] = total_checks
    report["fields_flagged_for_review"] = low_confidence_fields

    return report, Image.fromarray(seal_crop) if seal_crop is not None else None
