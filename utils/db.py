import json
import sqlite3
from datetime import datetime

DB_PATH = "ocr_app.db"


# =========================
# INIT DB
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        num_boxes INTEGER,
        texts TEXT,
        boxes TEXT,
        annotated_image TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# INSERT DOCUMENT
# =========================
def insert_document(file_name, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT INTO documents (
        file_name,
        num_boxes,
        texts,
        boxes,
        annotated_image,
        created_at
    ) VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            file_name,
            result["num_boxes"],
            json.dumps(result["texts"]),
            json.dumps(result["boxes"]),
            result["annotated_image"],
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()


# =========================
# GET ALL HISTORY
# =========================
def get_all_documents():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT file_name, num_boxes, texts, boxes, annotated_image, created_at
    FROM documents
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    results = []

    for r in rows:
        results.append(
            {
                "file_name": r[0],
                "num_boxes": r[1],
                "texts": json.loads(r[2]),
                "boxes": json.loads(r[3]),
                "annotated_image": r[4],
                "created_at": r[5],
            }
        )

    return results
