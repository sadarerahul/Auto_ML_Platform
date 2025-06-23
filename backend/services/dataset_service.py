# backend/services/dataset_service.py
import os, uuid
from backend.config import MAX_DATASETS, UPLOAD_DIR
from backend.utils import file_utils
from ..utils.regression.upload import save_uploaded_file
from backend.utils.regression.session_state import set_active_dataset

CLEANED_DATA_DIR = os.path.abspath("frontend/static/cleaned")


def _get_available_name(original: str) -> str:
    """Ensure no name conflict. Return available file name with .csv extension."""
    base, ext = os.path.splitext(original)
    base = base.replace(" ", "_")   # remove spaces
    candidate = f"{base}.csv"
    i = 1
    while os.path.exists(os.path.join(UPLOAD_DIR, candidate)):
        candidate = f"{base}({i}).csv"
        i += 1
    return candidate

# -------- public helpers --------
def list_files() -> list[str]:
    return file_utils.list_csv_files()

def can_upload() -> bool:
    return len(list_files()) < MAX_DATASETS

def upload_dataset(upload_file):
    """Return (df, message, blocked_flag). blocked_flag=True when limit hit or bad format."""
    name = upload_file.filename.lower()
    if   name.endswith(".csv"):            ftype = "csv"
    elif name.endswith((".xls", ".xlsx")): ftype = "excel"
    else:
        return None, "❌ Unsupported file format.", True

    if not can_upload():
        return None, f"⚠️ Limit of {MAX_DATASETS} datasets reached. Delete one to continue.", True

    final_name = _get_available_name(upload_file.filename)
    file_utils.save_raw_copy(upload_file, final_name)
    upload_file.file.seek(0)

    df, msg = save_uploaded_file(upload_file.file, ftype)
    blocked = df is None

    # ✅ Prevent re-cleaning cleaned datasets
    if final_name.endswith("_cleaned.csv"):
        set_active_dataset(final_name)
        return df, f"✅ Uploaded as {final_name} (already cleaned — no further cleaning applied)", blocked

    if df is not None:
        set_active_dataset(final_name)

    return df, f"✅ Uploaded as {final_name}" if df is not None else msg, blocked

def delete_files(filenames: list[str]):
    for filename in filenames:
        raw_path = os.path.join(UPLOAD_DIR, filename)
        cleaned_path = os.path.join(CLEANED_DATA_DIR, filename.replace(".csv", "_cleaned.csv"))

        if os.path.exists(raw_path):
            os.remove(raw_path)

        if os.path.exists(cleaned_path):
            os.remove(cleaned_path)
