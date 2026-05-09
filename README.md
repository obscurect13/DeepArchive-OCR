# 📄 DeepArchive OCR

An end-to-end **OCR platform that turns scanned documents into searchable, exportable PDFs** — with a REST API, interactive dashboard, and full Docker deployment.

## Features

- 🔍 **Automatic text detection** — EasyOCR detects and localizes text regions in any uploaded image
- 🖼 **Annotated preview** — bounding boxes drawn over detected regions displayed inline
- 📄 **Searchable PDF export** — original image as background with an invisible text overlay, making the output pixel-perfect and fully selectable/searchable
- 📚 **History** — all processed documents stored in SQLite with full-text search and CSV export
- 🟢 **API status indicator** — live health check displayed in the UI
- 🐳 **Fully containerized** — one `docker compose up --build` and everything runs
- ✅ **Unit tested** — pytest suite with coverage, linting with ruff, type checking with mypy, and CI via GitHub Actions

## Stack

| Layer | Technology |
|---|---|
| OCR Engine | EasyOCR |
| API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| PDF Generation | ReportLab |
| Database | SQLite |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-cov + pytest-mock |
| Linting / Types | ruff + mypy |
| CI/CD | GitHub Actions |

## Project Structure

```
deepArchive-OCR/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
├── api/
│   └── main.py                  # FastAPI endpoints (/health, /extract)
├── app/
│   └── streamlit_app.py         # Streamlit frontend
├── src/
│   ├── __init__.py
│   ├── pipeline.py              # OCR orchestrator
│   ├── detector.py              # Text region detection
│   ├── cropper.py               # Region cropping
│   └── ocr_engine.py            # EasyOCR text extraction
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_cropper.py          # Cropping unit tests
│   ├── test_detector.py         # Detection unit tests
│   ├── test_ocr_engine.py       # OCR engine unit tests
│   └── test_pipeline.py         # End-to-end pipeline tests
├── utils/
│   ├── db.py                    # SQLite persistence
│   └── document_generator.py   # PDF generation with searchable overlay
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## Getting Started

```bash
git clone https://github.com/your-username/deepArchive-OCR.git
cd deepArchive-OCR
docker compose up --build
```

- Streamlit UI → http://localhost:8501
- FastAPI Swagger → http://localhost:8000/docs

## Services

| Service | Description | Port |
|---|---|---|
| Streamlit | Interactive dashboard | 8501 |
| FastAPI | OCR API | 8000 |

## API

### `POST /extract`
Upload an image and receive detected bounding boxes, extracted texts, and an annotated image.

```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@invoice.png"
```

### `GET /health`
Returns `{"status": "ok"}` when the API is running.

## Author

**Omar SAID**
