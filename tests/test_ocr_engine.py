import pytest
import numpy as np
from unittest.mock import Mock, patch


def test_ocr_engine_init():
    """Test OCREngine initialization."""
    from src.ocr_engine import OCREngine

    with patch('src.ocr_engine.easyocr.Reader'):
        engine = OCREngine(languages=['en', 'fr'], gpu=False)
        assert engine.languages == ['en', 'fr']


def test_ocr_engine_default_languages():
    """Test OCREngine with default languages."""
    from src.ocr_engine import OCREngine

    with patch('src.ocr_engine.easyocr.Reader'):
        engine = OCREngine()
        assert engine.languages == ['en', 'fr']


def test_extract_text_success():
    """Test text extraction with mocked results."""
    from src.ocr_engine import OCREngine

    mock_reader = Mock()
    mock_reader.readtext.return_value = [
        ([0, 0, 10, 10], "Hello", 0.95),
        ([0, 10, 20, 20], "World", 0.88)
    ]

    with patch('src.ocr_engine.easyocr.Reader', return_value=mock_reader):
        engine = OCREngine()
        image = np.zeros((100, 100), dtype=np.uint8)
        results = engine.extract_text(image)

        assert len(results) == 2
        assert results[0]["text"] == "Hello"
        assert results[0]["confidence"] == 0.95
        assert results[1]["text"] == "World"
        assert results[1]["confidence"] == 0.88


def test_extract_text_empty():
    """Test text extraction with no results."""
    from src.ocr_engine import OCREngine

    mock_reader = Mock()
    mock_reader.readtext.return_value = []

    with patch('src.ocr_engine.easyocr.Reader', return_value=mock_reader):
        engine = OCREngine()
        image = np.zeros((100, 100), dtype=np.uint8)
        results = engine.extract_text(image)

        assert len(results) == 0


def test_extract_text_whitespace_filtering():
    """Test that whitespace-only text is filtered out."""
    from src.ocr_engine import OCREngine

    mock_reader = Mock()
    mock_reader.readtext.return_value = [
        ([0, 0, 10, 10], "   ", 0.95),  # Whitespace only
        ([0, 10, 20, 20], "Valid", 0.88)
    ]

    with patch('src.ocr_engine.easyocr.Reader', return_value=mock_reader):
        engine = OCREngine()
        image = np.zeros((100, 100), dtype=np.uint8)
        results = engine.extract_text(image)

        assert len(results) == 1
        assert results[0]["text"] == "Valid"


def test_extract_text_confidence_rounding():
    """Test confidence values are rounded to 4 decimal places."""
    from src.ocr_engine import OCREngine

    mock_reader = Mock()
    mock_reader.readtext.return_value = [
        ([0, 0, 10, 10], "Test", 0.987654321)
    ]

    with patch('src.ocr_engine.easyocr.Reader', return_value=mock_reader):
        engine = OCREngine()
        image = np.zeros((100, 100), dtype=np.uint8)
        results = engine.extract_text(image)

        assert results[0]["confidence"] == 0.9877
