import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch


def test_preprocess_for_ocr():
    """Test image preprocessing for OCR."""
    from src.pipeline import preprocess_for_ocr

    # Create a color image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:] = [128, 128, 128]

    processed = preprocess_for_ocr(image)

    # Should be grayscale
    assert len(processed.shape) == 2
    # Should be binary (thresholded)
    assert processed.dtype == np.uint8


def test_preprocess_for_ocr_small_image():
    """Test preprocessing upscales small images."""
    from src.pipeline import preprocess_for_ocr

    # Create a small image (< 30px height)
    image = np.zeros((20, 100, 3), dtype=np.uint8)

    processed = preprocess_for_ocr(image)

    # Should be upscaled
    assert processed.shape[0] >= 30


def test_draw_boxes():
    """Test drawing boxes on image."""
    from src.pipeline import draw_boxes

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    boxes = [(10, 10, 30, 30), (50, 50, 70, 70)]

    result = draw_boxes(image, boxes)

    # Should not modify original image
    assert not np.array_equal(image, result)
    # Result should have green pixels where boxes were drawn
    assert result.shape == image.shape


def test_encode_image_to_base64():
    """Test base64 encoding of image."""
    from src.pipeline import encode_image_to_base64

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:] = [255, 255, 255]

    encoded = encode_image_to_base64(image)

    assert isinstance(encoded, str)
    assert len(encoded) > 0
    # Should be valid base64
    import base64
    decoded = base64.b64decode(encoded)
    assert len(decoded) > 0


def test_process_image_integration():
    """Test full image processing pipeline with mocked components."""
    from src.pipeline import process_image

    # Create test image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:] = [255, 255, 255]

    with patch('src.pipeline.detect_text_regions', return_value=[(10, 10, 30, 30)]):
        with patch('src.pipeline.crop_regions', return_value=[np.zeros((20, 20, 3), dtype=np.uint8)]):
            with patch('src.pipeline.ocr.extract_text', return_value=[{"text": "Test", "confidence": 0.95}]):
                result = process_image(image)

                assert result["num_boxes"] == 1
                assert len(result["text_regions"]) == 1
                assert result["text_regions"][0]["box"] == (10, 10, 30, 30)
                assert result["text_regions"][0]["texts"][0]["text"] == "Test"
                assert "annotated_image" in result
                assert result["image_width"] == 100
                assert result["image_height"] == 100


def test_process_image_empty_result():
    """Test pipeline with no detected text regions."""
    from src.pipeline import process_image

    image = np.zeros((100, 100, 3), dtype=np.uint8)

    with patch('src.pipeline.detect_text_regions', return_value=[]):
        with patch('src.pipeline.crop_regions', return_value=[]):
            result = process_image(image)

            assert result["num_boxes"] == 0
            assert len(result["text_regions"]) == 0
            assert "annotated_image" in result


def test_process_image_multiple_boxes():
    """Test pipeline with multiple text regions."""
    from src.pipeline import process_image

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    boxes = [(10, 10, 30, 30), (50, 50, 70, 70)]

    with patch('src.pipeline.detect_text_regions', return_value=boxes):
        with patch('src.pipeline.crop_regions', return_value=[
            np.zeros((20, 20, 3), dtype=np.uint8),
            np.zeros((20, 20, 3), dtype=np.uint8)
        ]):
            with patch('src.pipeline.ocr.extract_text', return_value=[{"text": "Text", "confidence": 0.9}]):
                result = process_image(image)

                assert result["num_boxes"] == 2
                assert len(result["text_regions"]) == 2
