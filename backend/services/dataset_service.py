# backend/services/dataset_service.py

import os
from backend.config import MAX_DATASETS, UPLOAD_DIR
from backend.utils import file_utils
from backend.utils.regression.upload import save_uploaded_file
from backend.utils.regression.session_state import set_active_dataset
from backend.utils.regression.upload import clear_all_cache_for

# Cleaned datasets go here
CLEANED_DATA_DIR = os.path.abspath("frontend/static/cleaned")

# ───────────────────────────────────────────────────────────────
# 🔧 Internal Helper: Ensure unique dataset name
# ───────────────────────────────────────────────────────────────
def _get_available_name(original: str) -> str:
    """Make sure the uploaded file name is unique in uploads/."""
    base, ext = os.path.splitext(original)
    base = base.replace(" ", "_")
    candidate = f"{base}.csv"
    i = 1
    while os.path.exists(os.path.join(UPLOAD_DIR, candidate)):
        candidate = f"{base}({i}).csv"
        i += 1
    return candidate

# ───────────────────────────────────────────────────────────────
# 📋 List uploaded raw files
# ───────────────────────────────────────────────────────────────
def list_files() -> list[str]:
    return file_utils.list_csv_files()

# ───────────────────────────────────────────────────────────────
# 🚦 Check if user can upload more files
# ───────────────────────────────────────────────────────────────
def can_upload() -> bool:
    return len(list_files()) < MAX_DATASETS

# ───────────────────────────────────────────────────────────────
# 📤 Upload dataset and make it active
# ───────────────────────────────────────────────────────────────
def upload_dataset(upload_file):
    """
    Returns:
        - df: DataFrame or None
        - msg: success/failure message
        - blocked_flag: True if upload is blocked (limit hit or bad file)
    """
    name = upload_file.filename.lower()
    if name.endswith(".csv"):
        ftype = "csv"
    elif name.endswith((".xls", ".xlsx")):
        ftype = "excel"
    else:
        return None, "❌ Unsupported file format.", True

    if not can_upload():
        return None, f"⚠️ Limit of {MAX_DATASETS} datasets reached. Delete one to continue.", True

    # Generate safe and unique name
    final_name = _get_available_name(upload_file.filename)

    # Save original copy manually to disk
    file_utils.save_raw_copy(upload_file, final_name)
    upload_file.file.seek(0)  # Reset pointer for reading again

    # Load into pandas and activate
    df, msg = save_uploaded_file(upload_file.file, ftype)
    blocked = df is None

    if df is not None:
        set_active_dataset(final_name)

    return df, f"✅ Uploaded as {final_name}" if df is not None else msg, blocked

# ───────────────────────────────────────────────────────────────
# 🗑️ Delete dataset + all associated cleaned/model/split/etc.
# ───────────────────────────────────────────────────────────────
def delete_files(filenames: list[str]):
    for filename in filenames:
        raw_path     = os.path.join(UPLOAD_DIR, filename)
        cleaned_name = filename.replace(".csv", "_cleaned.csv")
        cleaned_path = os.path.join(CLEANED_DATA_DIR, cleaned_name)

        # Delete raw dataset
        if os.path.exists(raw_path):
            os.remove(raw_path)

        # Delete cleaned dataset
        if os.path.exists(cleaned_path):
            os.remove(cleaned_path)

        # 🔥 Wipe out all cached/generated artifacts
        clear_all_cache_for(filename)
