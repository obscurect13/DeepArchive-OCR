import base64

import cv2

from src.cropper import crop_regions
from src.detector import detect_text_regions
from src.ocr_engine import OCREngine

ocr = OCREngine()


def preprocess_for_ocr(crop):
    """Améliore la qualité du crop avant l'extraction de texte."""
    # 1. Passage en nuances de gris
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # 2. Augmentation du contraste (Denoising + Thresholding)
    # Utilisation du seuillage d'Otsu pour binariser l'image (Noir et Blanc pur)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. Redimensionnement si le crop est trop petit (optionnel mais recommandé)
    height, width = binary.shape
    if height < 30:
        binary = cv2.resize(binary, (None, None), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    return binary


def draw_boxes(image, boxes):
    for x1, y1, x2, y2 in boxes:
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return image


def encode_image_to_base64(image):
    _, buffer = cv2.imencode(".jpg", image)
    img_base64 = base64.b64encode(buffer).decode("utf-8")
    return img_base64


def process_image(image):
    # 1. Détection des régions
    boxes = detect_text_regions(image)

    # 2. Découpage des régions
    crops = crop_regions(image, boxes)

    text_regions = []

    for i, crop in enumerate(crops):
        # Prétraitement avant OCR
        processed_crop = preprocess_for_ocr(crop)

        # Extraction du texte sur l'image nettoyée
        extracted_texts = ocr.extract_text(processed_crop)
        box = boxes[i]
        text_regions.append({"box": box, "texts": extracted_texts})

    # 3. Annotation de l'image originale
    annotated = draw_boxes(image.copy(), boxes)

    # 4. Encodage
    annotated_base64 = encode_image_to_base64(annotated)

    return {
        "num_boxes": len(boxes),
        "text_regions": text_regions,
        "annotated_image": annotated_base64,
        "image_width": image.shape[1],
        "image_height": image.shape[0],
    }
