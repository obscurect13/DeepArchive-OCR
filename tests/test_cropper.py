import pytest
import numpy as np
import cv2


def test_crop_regions_basic():
    """Test basic crop functionality."""
    from src.cropper import crop_regions

    # Create a simple 100x100 image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:] = [255, 255, 255]  # White image

    boxes = [(10, 10, 30, 30), (50, 50, 70, 70)]
    crops = crop_regions(image, boxes)

    assert len(crops) == 2
    assert crops[0].shape == (24, 24, 3)  # 20x20 + 4 padding
    assert crops[1].shape == (24, 24, 3)


def test_crop_regions_with_padding():
    """Test crop with custom padding."""
    from src.cropper import crop_regions

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    boxes = [(10, 10, 30, 30)]

    crops = crop_regions(image, boxes, padding=10)
    assert len(crops) == 1
    assert crops[0].shape == (40, 40, 3)  # 20x20 + 10 padding


def test_crop_regions_boundary():
    """Test crop respects image boundaries."""
    from src.cropper import crop_regions

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    # Box at edge of image
    boxes = [(0, 0, 20, 20)]

    crops = crop_regions(image, boxes, padding=10)
    assert len(crops) == 1
    # Should not exceed image bounds
    assert crops[0].shape[0] <= 100
    assert crops[0].shape[1] <= 100


def test_crop_regions_empty_boxes():
    """Test crop with empty boxes list."""
    from src.cropper import crop_regions

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    crops = crop_regions(image, [])

    assert len(crops) == 0


def test_crop_regions_invalid_box():
    """Test crop filters out invalid boxes."""
    from src.cropper import crop_regions

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    # Invalid box (x2 < x1)
    boxes = [(30, 10, 10, 30)]

    crops = crop_regions(image, boxes)
    # Should still return a crop, even if coordinates are swapped
    assert len(crops) == 1
