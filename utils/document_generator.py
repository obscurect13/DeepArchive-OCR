"""
utils/document_generator.py
Generates PDF and DOCX files from OCR extraction results.
Texts are placed spatially according to their bounding box positions.
"""
import io
import base64

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# ============================================================
# IMAGE-BASED RECONSTRUCTION (pixel-perfect)
# ============================================================

def generate_pdf_from_image(
    annotated_image_b64: str,
    texts: list[dict] = None,
    image_width: int = None,
    image_height: int = None
) -> bytes:
    """
    Generate a searchable PDF:
    - Original image as pixel-perfect background
    - Invisible text overlay at exact bounding box positions so text is selectable/copyable

    Args:
        annotated_image_b64: Base64-encoded image
        texts:               List of dicts with keys: text, box, confidence
        image_width:         Source image width in pixels
        image_height:        Source image height in pixels

    Returns:
        PDF as bytes
    """
    from reportlab.lib.utils import ImageReader

    img_bytes = io.BytesIO(base64.b64decode(annotated_image_b64))
    reader = ImageReader(img_bytes)
    img_w, img_h = reader.getSize()

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(img_w, img_h))

    # --- Background: original image ---
    img_bytes.seek(0)
    c.drawImage(ImageReader(img_bytes), 0, 0, width=img_w, height=img_h)

    # --- Invisible text overlay ---
    if texts and image_width and image_height:
        scale_x = img_w / image_width
        scale_y = img_h / image_height

        # Fully transparent text — visible to PDF readers for selection/search
        c.setFillColorRGB(0, 0, 0, alpha=0)

        for item in texts:
            text = item.get("text", "").strip()
            box = item.get("box")
            if not text or not box:
                continue

            x1, y1, x2, y2 = box

            # Scale box to PDF canvas size
            pdf_x = x1 * scale_x
            pdf_y = img_h - (y2 * scale_y)   # flip Y axis (PDF origin = bottom-left)

            box_w = (x2 - x1) * scale_x
            box_h = (y2 - y1) * scale_y
            font_size = max(4, min(int(box_h * 0.85), 32))

            c.setFont("Helvetica", font_size)

            # Scale text to fit box width exactly
            try:
                text_w = c.stringWidth(text, "Helvetica", font_size)
                if text_w > 0:
                    c.saveState()
                    c.transform(box_w / text_w, 0, 0, 1, pdf_x, pdf_y)
                    c.drawString(0, 0, text)
                    c.restoreState()
                else:
                    c.drawString(pdf_x, pdf_y, text)
            except Exception:
                c.drawString(pdf_x, pdf_y, text)

    c.save()
    return pdf_buffer.getvalue()

# ============================================================
# HELPERS
# ============================================================

def _estimate_font_size(box: list, min_size: int = 7, max_size: int = 32) -> int:
    """Estimate font size from bounding box height."""
    x1, y1, x2, y2 = box
    height = y2 - y1
    return max(min_size, min(max_size, int(height * 0.72)))


def _sort_texts_top_to_bottom(texts: list[dict]) -> list[dict]:
    """Sort text items top-to-bottom, left-to-right using their box positions."""
    return sorted(texts, key=lambda t: (t["box"][1], t["box"][0]))


# ============================================================
# PDF GENERATION
# ============================================================

def generate_pdf_with_layout(
    texts: list[dict],
    image_width: int,
    image_height: int
) -> bytes:
    """
    Generate a clean PDF with text placed proportionally
    to its original position in the source image.

    Args:
        texts:         List of dicts with keys: text, box, confidence
        image_width:   Source image width in pixels
        image_height:  Source image height in pixels

    Returns:
        PDF as bytes
    """
    page_w, page_h = A4  # 595 x 842 pt

    scale_x = page_w / image_width
    scale_y = page_h / image_height

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # White background
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)

    sorted_texts = _sort_texts_top_to_bottom(texts)

    for item in sorted_texts:
        text = item.get("text", "").strip()
        box = item.get("box")
        if not text or not box:
            continue

        x1, y1, x2, y2 = box
        font_size = _estimate_font_size(box)

        # Convert image coords → PDF coords (flip Y axis)
        pdf_x = x1 * scale_x
        pdf_y = page_h - (y2 * scale_y)

        c.setFont("Helvetica", font_size)
        c.drawString(pdf_x, pdf_y, text)

    c.save()
    return pdf_buffer.getvalue()