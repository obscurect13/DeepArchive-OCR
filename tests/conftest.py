import pytest
import numpy as np


@pytest.fixture
def sample_image():
    """Create a sample 100x100 white image."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:] = [255, 255, 255]
    return image


@pytest.fixture
def sample_boxes():
    """Create sample bounding boxes."""
    return [(10, 10, 30, 30), (50, 50, 70, 70)]


@pytest.fixture
def sample_text_regions():
    """Create sample text regions."""
    return [
        {"text": "Hello", "confidence": 0.95},
        {"text": "World", "confidence": 0.88},
    ]
