import pytesseract
from PIL import Image, ImageOps
import io

def preprocess_image(image_bytes):
    """Gri tonlama ve eşikleme ile OCR başarısını artır."""
    img = Image.open(io.BytesIO(image_bytes)).convert("L")  # gri
    img = ImageOps.autocontrast(img)                         # kontrast artır
    # Eşikleme (isteğe bağlı)
    # img = img.point(lambda x: 0 if x < 128 else 255, '1')
    return img

def ocr_turkish(image_bytes):
    """Türkçe OCR, ön işleme ile."""
    img = preprocess_image(image_bytes)
    text = pytesseract.image_to_string(img, lang='tur')
    return text
