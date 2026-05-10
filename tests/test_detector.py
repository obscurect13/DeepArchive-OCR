from unittest.mock import patch

import numpy as np


@patch("src.detector._reader.detect")
def test_detect_text_regions_success(mock_detect):
    from src.detector import detect_text_regions

    # Simulate EasyOCR returning two horizontal boxes: [x1, x2, y1, y2]
    mock_detect.return_value = ([[10, 50, 10, 30], [60, 90, 40, 60]], [])

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    boxes = detect_text_regions(image)

    assert len(boxes) == 2
    assert boxes[0] == (10, 10, 50, 30)  # Converted to (x1, y1, x2, y2)


def test_detect_text_regions_empty():
    """Test text detection with no results."""
    from src.detector import detect_text_regions

    with patch("src.detector._reader.detect", return_value=None):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 0


def test_detect_text_regions_no_horizontal_boxes():
    """Test text detection when no horizontal boxes found."""
    from src.detector import detect_text_regions

    mock_result = [None, None]

    with patch("src.detector._reader.detect", return_value=mock_result):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 0


def test_detect_text_regions_filters_degenerate():
    """Test that degenerate boxes are filtered out."""
    from src.detector import detect_text_regions

    mock_result = [
        [
            [[10, 20], [30, 20], [30, 40], [10, 40]],  # Valid box
            [[10, 20], [10, 20], [10, 20], [10, 20]],  # Degenerate (x2 == x1)
            [[10, 20], [30, 20], [30, 20], [10, 20]],  # Degenerate (y2 == y1)
        ],
        None,
    ]

    with patch("src.detector._reader.detect", return_value=mock_result):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 1
        assert boxes[0] == (10, 20, 30, 40)


@patch("src.detector._reader.detect")
def test_detect_text_regions_box_format(mock_detect):
    from src.detector import detect_text_regions

    # Mock EasyOCR returning one valid horizontal box
    mock_detect.return_value = ([[10, 50, 20, 60]], [])

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    boxes = detect_text_regions(image)

    assert len(boxes) == 1
    assert boxes[0] == (10, 20, 50, 60)
