import fitz
from PIL import Image
import io
import numpy as np
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images

def extract_text_with_boxes(image):
    max_width, max_height = 1600, 2000
    image = image.copy()
    if image.width > max_width or image.height > max_height:
        image.thumbnail((max_width, max_height))

    image_np = np.array(image)
    results = reader.readtext(image_np)
    return [{"text": text, "bbox": bbox, "conf": conf} for (bbox, text, conf) in results]
