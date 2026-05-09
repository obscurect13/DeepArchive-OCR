import numpy as np
import cv2
import io
import logging
import time

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from PIL import Image
from src.pipeline import process_image

# =========================
# LOGGER SETUP
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("deeparchive.api")

# =========================
# APP
# =========================
app = FastAPI(
    title="OCR YOLO API",
    version="2.0"
)


# =========================
# MIDDLEWARE - Request logging
# =========================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"← {request.method} {request.url.path} [{response.status_code}] {duration}ms")
    return response


# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
async def health():
    logger.debug("Health check called")
    return {"status": "ok"}


# =========================
# EXTRACT ENDPOINT
# =========================
@app.post("/extract")
async def extract(file: UploadFile = File(...)):

    logger.info(f"Received file: '{file.filename}' | content_type: {file.content_type}")

    # ------------------------
    # READ IMAGE
    # ------------------------
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_np = np.array(image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        logger.info(f"Image loaded: {image_cv.shape[1]}x{image_cv.shape[0]}px")
    except Exception as e:
        logger.error(f"Failed to read image: {e}")
        return JSONResponse(status_code=400, content={"error": f"Invalid image: {e}"})

    # ------------------------
    # PIPELINE
    # ------------------------
    try:
        t0 = time.time()
        result = process_image(image_cv)
        elapsed = round((time.time() - t0) * 1000, 2)
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Pipeline failed: {e}"})

    # ------------------------
    # FLATTEN text_regions → texts + boxes
    # ------------------------
    texts = []
    boxes = []
    for region in result["text_regions"]:
        box = region["box"]
        boxes.append(box)
        for text_item in region["texts"]:
            texts.append({
                "text": text_item["text"],
                "confidence": text_item.get("confidence", 0.0),
                "box": box
            })

    logger.info(
        f"Pipeline complete: {result['num_boxes']} boxes, "
        f"{len(texts)} texts extracted in {elapsed}ms"
    )

    # ------------------------
    # RESPONSE
    # ------------------------
    return {
        "status": "success",
        "num_boxes": result["num_boxes"],
        "texts": texts,
        "boxes": boxes,
        "text_regions": result["text_regions"],
        "annotated_image": result["annotated_image"],
        "image_width": result["image_width"],
        "image_height": result["image_height"]
    }
