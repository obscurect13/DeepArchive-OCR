import easyocr
import numpy as np


class OCREngine:
    """
    Wraps EasyOCR to extract text from cropped image regions.
    The reader is initialized once and reused across all calls.
    """

    def __init__(self, languages: list[str] | None = None, gpu: bool = False):
        self.languages = languages or ["en", "fr"]
        self.reader = easyocr.Reader(self.languages, gpu=gpu)

    def extract_text(self, image: np.ndarray) -> list[dict]:
        """
        Extract text from a single image crop.

        Args:
            image: Grayscale or BGR image as numpy array

        Returns:
            List of dicts with keys: text, confidence
        """
        results = self.reader.readtext(image, detail=1)

        extracted = []
        for _, text, confidence in results:
            text = text.strip()
            if text:
                extracted.append({"text": text, "confidence": round(float(confidence), 4)})

        return extracted
