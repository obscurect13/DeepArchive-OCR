# Tests

This directory contains unit tests for the deepArchive-OCR project.

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_cropper.py
```

### Run specific test
```bash
pytest tests/test_cropper.py::test_crop_regions_basic
```

### Run with verbose output
```bash
pytest -v
```

## Test Structure

- `test_cropper.py` - Tests for image cropping functionality
- `test_detector.py` - Tests for text region detection
- `test_ocr_engine.py` - Tests for OCR text extraction
- `test_pipeline.py` - Tests for the complete processing pipeline

## CI/CD

Tests are automatically run on GitHub Actions for every push and pull request to `main` and `develop` branches.

The CI pipeline includes:
- Python 3.10, 3.11, and 3.12 testing
- Linting with ruff
- Type checking with mypy
- Docker build verification
