import base64
import logging
import os

import pandas as pd
import requests
import streamlit as st

from utils.db import get_all_documents, init_db, insert_document
from utils.document_generator import generate_pdf_from_image

# =========================
# LOGGER SETUP
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("deeparchive.frontend")

# =========================
# CONFIG
# =========================
API_URL = os.getenv("API_URL", "http://localhost:8000/extract")
API_HEALTH_URL = API_URL.replace("/extract", "/health")

# =========================
# INIT DB
# =========================
init_db()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="DeepArchive OCR", page_icon="📄", layout="wide")


# =========================
# UTILS
# =========================
def decode_image(img_base64):
    return base64.b64decode(img_base64)


def check_api_status() -> bool:
    try:
        r = requests.get(API_HEALTH_URL, timeout=2)
        return r.status_code == 200
    except Exception:
        return False


# =========================
# HEADER
# =========================
api_online = check_api_status()

if api_online:
    logger.info("API health check passed")
else:
    logger.warning("API health check failed — API is unreachable")

header_col, status_col = st.columns([4, 1])
with header_col:
    st.title("📄 DeepArchive OCR")
with status_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if api_online:
        st.success("🟢 API Online")
    else:
        st.error("🔴 API Offline")

# =========================
# NAVIGATION
# =========================
if "page" not in st.session_state:
    st.session_state.page = "upload"

nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    if st.button("📤 Upload", use_container_width=True):
        st.session_state.page = "upload"
with nav_col2:
    if st.button("📚 History", use_container_width=True):
        st.session_state.page = "history"

st.markdown("---")

page = st.session_state.page


# ============================================================
# 📤 UPLOAD PAGE
# ============================================================
if page == "upload":
    st.title("📤 Upload Document")

    if not api_online:
        st.warning("⚠️ The API is currently offline. Upload is disabled until it comes back online.")
        st.stop()

    uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        logger.info(f"User uploaded file: {uploaded_file.name}")
        st.image(uploaded_file, width="stretch")

        with st.spinner("Processing OCR..."):
            try:
                response = requests.post(API_URL, files={"file": uploaded_file})
                response.raise_for_status()
                result = response.json()
                logger.info(
                    f"OCR complete for '{uploaded_file.name}': "
                    f"{result['num_boxes']} boxes, {len(result['texts'])} texts"
                )
            except requests.exceptions.ConnectionError:
                logger.error("Connection refused when calling API /extract")
                st.error("Cannot reach the API. Make sure the API container is running.")
                st.stop()
            except requests.exceptions.HTTPError as e:
                logger.error(f"API HTTP error: {e}")
                st.error(f"API returned an error: {e}")
                st.stop()
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                st.error(f"Unexpected error: {e}")
                st.stop()

        insert_document(uploaded_file.name, result)
        st.success("Saved to database ✔")

        # -------------------------
        # DOWNLOAD BUTTONS
        # -------------------------
        st.subheader("📥 Export Extracted Document")

        try:
            pdf_bytes = generate_pdf_from_image(
                result["annotated_image"],
                texts=result["texts"],
                image_width=result.get("image_width"),
                image_height=result.get("image_height"),
            )
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_bytes,
                file_name=f"{uploaded_file.name}_extracted.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            logger.error(f"PDF generation error: {e}", exc_info=True)
            st.error(f"PDF generation failed: {e}")

        st.markdown("---")

        # -------------------------
        # RESULTS
        # -------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Detected Boxes", result["num_boxes"])

            st.subheader("🧠 Extracted Text")
            if result["texts"]:
                for t in result["texts"]:
                    st.write(f"- {t['text']}")
            else:
                st.info("No text detected.")

        with col2:
            st.subheader("🖼 Annotated Image")
            img = decode_image(result["annotated_image"])
            st.image(img)


# ============================================================
# 📚 HISTORY PAGE
# ============================================================
elif page == "history":
    st.title("📚 Processing History")

    history = get_all_documents()
    logger.info(f"History page loaded: {len(history)} records")

    if not history:
        st.warning("No documents found in database.")
    else:
        search_query = st.text_input("🔍 Search in documents (filename or content)", "")

        filtered_history = []
        for item in history:
            content_text = " ".join([t["text"] for t in item["texts"]]).lower()
            if (
                search_query.lower() in item["file_name"].lower()
                or search_query.lower() in content_text
            ):
                filtered_history.append(item)

        if filtered_history:
            df_export = pd.DataFrame(
                [
                    {
                        "Date": i["created_at"],
                        "Filename": i["file_name"],
                        "Full Text": " | ".join([t["text"] for t in i["texts"]]),
                    }
                    for i in filtered_history
                ]
            )
            st.download_button(
                label="📥 Export results to CSV",
                data=df_export.to_csv(index=False).encode("utf-8"),
                file_name="ocr_history_export.csv",
                mime="text/csv",
            )

        st.markdown(f"**Found {len(filtered_history)} documents**")

        for item in filtered_history:
            with st.expander(f"📄 {item['file_name']} (Created: {item['created_at'][:10]})"):
                col_view, col_edit = st.columns(2)

                with col_view:
                    st.write("### 🖼 Annotated Image")
                    img = base64.b64decode(item["annotated_image"])
                    st.image(img)

                with col_edit:
                    st.write("### 🧠 Extracted Text")
                    combined_text = "\n".join([t["text"] for t in item["texts"]])
                    st.text_area(
                        "Edit/Copy text:",
                        value=combined_text,
                        height=250,
                        key=f"edit_{item['created_at']}",
                    )

                    # Re-generate exports from history
                    if item.get("annotated_image"):
                        try:
                            pdf_bytes = generate_pdf_from_image(
                                item["annotated_image"],
                                texts=item.get("texts"),
                                image_width=item.get("image_width"),
                                image_height=item.get("image_height"),
                            )
                            st.download_button(
                                "📄 PDF",
                                data=pdf_bytes,
                                file_name=f"{item['file_name']}_extracted.pdf",
                                mime="application/pdf",
                                key=f"pdf_{item['created_at']}",
                            )
                        except Exception:
                            pass

                st.write("### 📦 Bounding Boxes")
                st.json(item["boxes"])
