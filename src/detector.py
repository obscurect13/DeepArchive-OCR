import easyocr
import numpy as np

_reader = easyocr.Reader(["en", "fr"], gpu=False)


def detect_text_regions(image: np.ndarray) -> list[tuple[int, int, int, int]]:
    results = _reader.detect(image)
    boxes = []

    if results and results[0]:
        for bbox in results[0]:

            # Format polygon EasyOCR:
            # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            if isinstance(bbox[0], (list, tuple)):
                xs = [point[0] for point in bbox]
                ys = [point[1] for point in bbox]

                x1 = int(min(xs))
                x2 = int(max(xs))
                y1 = int(min(ys))
                y2 = int(max(ys))

            # Format simple:
            # [x1, x2, y1, y2]
            else:
                x1 = int(bbox[0])
                x2 = int(bbox[1])
                y1 = int(bbox[2])
                y2 = int(bbox[3])

            # Filter degenerate boxes
            if x2 > x1 and y2 > y1:
                boxes.append((x1, y1, x2, y2))

    return boxes