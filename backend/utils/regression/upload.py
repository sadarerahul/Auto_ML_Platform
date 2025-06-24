import os
import pandas as pd
from io import BytesIO
from fastapi import UploadFile
from fastapi.templating import Jinja2Templates

# 📁 Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend"))
UPLOAD_DIR = os.path.join(FRONTEND_DIR, "static/uploads")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
ACTIVE_DATASET_PATH = os.path.join(UPLOAD_DIR, "active_dataset.txt")

# ✅ Hidden backend directory for cleaned datasets
CLEANED_DATA_DIR = os.path.abspath(os.path.join(FRONTEND_DIR, "static/cleaned"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)

templates = Jinja2Templates(directory=TEMPLATE_DIR)
MAX_ROWS = 500

# --------------------------------------------
# ✅ Track active dataset
# --------------------------------------------
def set_active_dataset(filename: str):
    with open(ACTIVE_DATASET_PATH, "w") as f:
        f.write(filename.strip())

def get_active_dataset() -> str:
    if os.path.exists(ACTIVE_DATASET_PATH):
        with open(ACTIVE_DATASET_PATH, "r") as f:
            return f.read().strip()
    return ""

# --------------------------------------------
# ✅ Get data paths for a given filename
# --------------------------------------------
def _get_data_paths(filename: str):
    original = os.path.join(UPLOAD_DIR, filename)
    cleaned_name = filename.replace(".csv", "_cleaned.csv")
    cleaned = os.path.join(CLEANED_DATA_DIR, cleaned_name)
    return original, cleaned

# --------------------------------------------
# ✅ Save uploaded file and activate it
# --------------------------------------------
async def save_uploaded_file(file: UploadFile, file_type="csv"):
    try:
        file_bytes = await file.read()
        buffer = BytesIO(file_bytes)

        if file_type == "csv":
            df = pd.read_csv(buffer)
        elif file_type == "excel":
            df = pd.read_excel(buffer, engine="openpyxl")
        else:
            raise ValueError("Unsupported file format")

        df = df.head(MAX_ROWS)
        filename = file.filename
        original_path, cleaned_path = _get_data_paths(filename)

        # ✅ Save original file
        df.to_csv(original_path, index=False)

        # ✅ ALSO save it as 'recent.csv' so EDA can use it
        recent_path = os.path.join(UPLOAD_DIR, "recent.csv")
        df.to_csv(recent_path, index=False)

        # ✅ Track the active dataset for sidebar context
        set_active_dataset(filename)
        return df, "✅ File uploaded successfully!"
    except Exception:
        return None, "❌ Error uploading file"

# --------------------------------------------
# ✅ Return column names from active dataset
# --------------------------------------------
def get_column_names():
    try:
        filename = get_active_dataset()
        if not filename:
            return []
        path, _ = _get_data_paths(filename)
        df = pd.read_csv(path)
        return df.columns.tolist()
    except Exception:
        return []

# --------------------------------------------
# ✅ Return preview table as HTML
# --------------------------------------------
def get_head_as_html(n=10):
    try:
        filename = get_active_dataset()
        if not filename:
            return "<p class='text-warning'>⚠️ No active dataset selected.</p>"
        path, _ = _get_data_paths(filename)
        df = pd.read_csv(path)
        return df.head(n).to_html(classes="table table-striped table-bordered", index=False)
    except Exception as e:
        return f"<p class='text-danger'>❌ Failed to load preview: {str(e)}</p>"

# --------------------------------------------
# ✅ List all datasets available
# --------------------------------------------
def list_uploaded_datasets():
    return [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv") and not f.endswith("_cleaned.csv")
    ]