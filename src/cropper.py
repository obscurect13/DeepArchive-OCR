import numpy as np


def crop_regions(
    image: np.ndarray,
    boxes: list[tuple[int, int, int, int]],
    padding: int = 4
) -> list[np.ndarray]:
    """
    Crop regions from an image using bounding boxes.

    Args:
        image:   BGR image as numpy array (OpenCV format)
        boxes:   List of (x1, y1, x2, y2) bounding boxes
        padding: Extra pixels to include around each box

    Returns:
        List of cropped image regions as numpy arrays
    """
    h, w = image.shape[:2]
    crops = []

    for (x1, y1, x2, y2) in boxes:
        # Apply padding while staying within image boundaries
        x1p = max(0, x1 - padding)
        y1p = max(0, y1 - padding)
        x2p = min(w, x2 + padding)
        y2p = min(h, y2 + padding)

        crop = image[y1p:y2p, x1p:x2p]

        if crop.size > 0:
            crops.append(crop)

    return crops
