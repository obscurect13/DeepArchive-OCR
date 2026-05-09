import easyocr
import numpy as np

# Initialize once at module level to avoid reloading the model on every call
_reader = easyocr.Reader(['en', 'fr'], gpu=False)


def detect_text_regions(image: np.ndarray) -> list[tuple[int, int, int, int]]:
    """
    Detect text regions in an image and return bounding boxes.

    Args:
        image: BGR image as numpy array (OpenCV format)

    Returns:
        List of bounding boxes as (x1, y1, x2, y2) tuples
    """
    results = _reader.detect(image)

    boxes = []

    # results[0] contains horizontal text boxes
    if results and results[0]:
        for bbox in results[0][0]:
            x1 = int(bbox[0])
            y1 = int(bbox[2])
            x2 = int(bbox[1])
            y2 = int(bbox[3])

            # Filter out degenerate boxes
            if x2 > x1 and y2 > y1:
                boxes.append((x1, y1, x2, y2))

    return boxes
