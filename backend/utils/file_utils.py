# backend/utils/file_utils.py

import os
import shutil
import logging
from backend.config import UPLOAD_DIR

# Create upload directory if not present
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Setup logger for debug info (optional)
logger = logging.getLogger(__name__)

def get_path(filename: str) -> str:
    """Helper: Full path of a file in the upload directory."""
    return os.path.join(UPLOAD_DIR, filename)

def list_csv_files():
    """
    List all CSV files in the uploads/ directory except 'uploaded_data.csv',
    sorted by latest modified first.
    """
    csvs = [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv") and f != "uploaded_data.csv"
    ]
    return sorted(csvs, key=lambda f: os.path.getmtime(get_path(f)), reverse=True)

def save_raw_copy(upload_file, unique_name: str):
    """
    Save uploaded file stream to uploads/ with the specified unique name.
    Streams file instead of reading it all into memory.
    """
    full_path = get_path(unique_name)
    with open(full_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)  # ✅ memory-safe
    logger.info(f"✅ Saved file: {unique_name}")

def delete_files(filenames: list[str]):
    """
    Delete files by name from the uploads/ directory if they exist.
    """
    for fname in filenames:
        path = get_path(fname)
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"🗑️ Deleted file: {fname}")
        else:
            logger.warning(f"⚠️ File not found: {fname}")

def file_exists(filename: str) -> bool:
    """
    Check if a file exists in the uploads/ directory.
    """
    return os.path.exists(get_path(filename))
