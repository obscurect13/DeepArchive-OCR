import pytest
import numpy as np
from unittest.mock import Mock, patch


def test_detect_text_regions_success():
    """Test text detection with mocked results."""
    from src.detector import detect_text_regions

    # Mock EasyOCR detect result
    # results[0] contains horizontal text boxes
    mock_result = [
        [  # Horizontal boxes
            [[10, 20], [30, 20], [30, 40], [10, 40]],  # Box 1
            [[50, 60], [70, 60], [70, 80], [50, 80]]   # Box 2
        ],
        None  # Free boxes (not used)
    ]

    with patch('src.detector._reader.detect', return_value=mock_result):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 2
        assert boxes[0] == (10, 20, 30, 40)
        assert boxes[1] == (50, 60, 70, 80)


def test_detect_text_regions_empty():
    """Test text detection with no results."""
    from src.detector import detect_text_regions

    with patch('src.detector._reader.detect', return_value=None):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 0


def test_detect_text_regions_no_horizontal_boxes():
    """Test text detection when no horizontal boxes found."""
    from src.detector import detect_text_regions

    mock_result = [None, None]

    with patch('src.detector._reader.detect', return_value=mock_result):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 0


def test_detect_text_regions_filters_degenerate():
    """Test that degenerate boxes are filtered out."""
    from src.detector import detect_text_regions

    mock_result = [
        [
            [[10, 20], [30, 20], [30, 40], [10, 40]],  # Valid box
            [[10, 20], [10, 20], [10, 20], [10, 20]],  # Degenerate (x2 == x1)
            [[10, 20], [30, 20], [30, 20], [10, 20]]   # Degenerate (y2 == y1)
        ],
        None
    ]

    with patch('src.detector._reader.detect', return_value=mock_result):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 1
        assert boxes[0] == (10, 20, 30, 40)


def test_detect_text_regions_box_format():
    """Test that box coordinates are correctly formatted."""
    from src.detector import detect_text_regions

    # EasyOCR returns: [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
    mock_result = [
        [
            [[5, 10], [15, 10], [15, 20], [5, 20]]
        ],
        None
    ]

    with patch('src.detector._reader.detect', return_value=mock_result):
        boxes = detect_text_regions(np.zeros((100, 100, 3), dtype=np.uint8))

        assert len(boxes) == 1
        # Should return (x1, y1, x2, y2)
        assert boxes[0] == (5, 10, 15, 20)
