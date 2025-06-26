import os
import pandas as pd
from io import BytesIO
from fastapi import UploadFile
from fastapi.templating import Jinja2Templates
import logging

# 📁 Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend"))

UPLOAD_DIR = os.path.join(FRONTEND_DIR, "static", "uploads")
CLEANED_DATA_DIR = os.path.join(FRONTEND_DIR, "static", "cleaned")
PROCESSED_DIR = os.path.join(FRONTEND_DIR, "static", "processed")
PREDICTIONS_DIR = os.path.join(FRONTEND_DIR, "static", "predictions")
MODELS_DIR = os.path.join(FRONTEND_DIR, "static", "models")
SPLIT_DIR = os.path.join(FRONTEND_DIR, "static", "splits")
PLOTS_DIR = os.path.join(FRONTEND_DIR, "static", "plots")

TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
ACTIVE_DATASET_PATH = os.path.join(UPLOAD_DIR, "active_dataset.txt")

# ✅ Ensure all required folders exist
for folder in [
    UPLOAD_DIR, CLEANED_DATA_DIR, PROCESSED_DIR,
    PREDICTIONS_DIR, MODELS_DIR, SPLIT_DIR, PLOTS_DIR
]:
    os.makedirs(folder, exist_ok=True)

# ✅ Setup templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)
MAX_ROWS = 500
logging.basicConfig(level=logging.INFO)

# ───────────────────────────────────────────────
# ✅ Active Dataset State
# ───────────────────────────────────────────────
def set_active_dataset(filename: str):
    name_only = os.path.basename(filename)
    with open(ACTIVE_DATASET_PATH, "w", encoding="utf-8") as f:
        f.write(name_only.strip())
    logging.info(f"✅ Active dataset set to: {name_only}")

def get_active_dataset() -> str:
    if os.path.exists(ACTIVE_DATASET_PATH):
        with open(ACTIVE_DATASET_PATH, "r", encoding="utf-8") as f:
            dataset_name = f.read().strip()
            dataset_path = os.path.join(UPLOAD_DIR, dataset_name)
            if os.path.exists(dataset_path):
                return dataset_name
            else:
                os.remove(ACTIVE_DATASET_PATH)
    return ""

def get_active_dataset_path():
    filename = get_active_dataset()
    return os.path.join(UPLOAD_DIR, filename) if filename else None

def is_dataset_active(filename):
    return os.path.basename(filename) == get_active_dataset()

# ───────────────────────────────────────────────
# ✅ Upload File + Save
# ───────────────────────────────────────────────
def _get_available_name(filename):
    base, ext = os.path.splitext(filename)
    i = 1
    candidate = filename
    while os.path.exists(os.path.join(UPLOAD_DIR, candidate)):
        candidate = f"{base}({i}){ext}"
        i += 1
    return candidate

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
        filename = _get_available_name(file.filename)
        original_path = os.path.join(UPLOAD_DIR, filename)
        df.to_csv(original_path, index=False, encoding="utf-8")
        set_active_dataset(filename)

        return df, f"✅ Uploaded as {filename}"
    except Exception as e:
        return None, f"❌ Upload failed: {str(e)}"

# ───────────────────────────────────────────────
# ✅ Dataset Metadata Helpers
# ───────────────────────────────────────────────
def get_column_names():
    try:
        path = get_active_dataset_path()
        if not path:
            return []
        df = pd.read_csv(path)
        return df.columns.tolist()
    except Exception:
        return []

def get_head_as_html(n=10):
    try:
        path = get_active_dataset_path()
        if not path:
            return "<p class='text-danger'>❌ Active dataset not found. Please upload or select another.</p>"
        df = pd.read_csv(path)
        return df.head(n).to_html(classes="table table-striped table-bordered", index=False)
    except Exception as e:
        return f"<p class='text-danger'>❌ Failed to load preview: {str(e)}</p>"

# ───────────────────────────────────────────────
# ✅ Listing Datasets
# ───────────────────────────────────────────────
def list_uploaded_datasets():
    return [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv") and not f.endswith("_cleaned.csv")
    ]

# ───────────────────────────────────────────────
# ✅ Deletion Utilities
# ───────────────────────────────────────────────
def _delete_files_by_prefix_and_ext(dir_path, prefix, ext):
    for f in os.listdir(dir_path):
        if f.startswith(prefix) and f.endswith(ext):
            try:
                os.remove(os.path.join(dir_path, f))
            except Exception as e:
                print(f"⚠️ Could not delete file {f} from {dir_path}: {e}")

def delete_related_processed_files(dataset_name: str):
    base = os.path.splitext(dataset_name)[0]
    _delete_files_by_prefix_and_ext(PROCESSED_DIR, base, ".csv")

def delete_related_prediction_files(dataset_name: str):
    base = os.path.splitext(dataset_name)[0]
    _delete_files_by_prefix_and_ext(PREDICTIONS_DIR, base, ".csv")

def delete_related_model_files(dataset_name: str):
    base = os.path.splitext(dataset_name)[0]
    _delete_files_by_prefix_and_ext(MODELS_DIR, base, ".pkl")

def delete_related_split_files(dataset_name: str):
    base = os.path.splitext(dataset_name)[0]
    _delete_files_by_prefix_and_ext(SPLIT_DIR, base, ".csv")

def delete_related_plot_files(dataset_name: str):
    base = os.path.splitext(dataset_name)[0]
    if base.endswith("_cleaned"):
        base = base.replace("_cleaned", "")

    for f in os.listdir(PLOTS_DIR):
        if f.startswith(base):
            try:
                os.remove(os.path.join(PLOTS_DIR, f))
            except Exception as e:
                print(f"⚠️ Could not delete plot file {f} from {PLOTS_DIR}: {e}")

def delete_cleaned_version(dataset_name: str):
    base = os.path.splitext(dataset_name)[0]
    cleaned_file = f"{base}_cleaned.csv"
    cleaned_path = os.path.join(CLEANED_DATA_DIR, cleaned_file)

    if os.path.exists(cleaned_path):
        try:
            os.remove(cleaned_path)
            print(f"🗑️ Deleted cleaned dataset: {cleaned_file}")
        except Exception as e:
            print(f"⚠️ Could not delete cleaned file {cleaned_file}: {e}")

def clear_all_cache_for(filename: str):
    delete_related_processed_files(filename)
    delete_related_prediction_files(filename)
    delete_related_model_files(filename)
    delete_related_split_files(filename)
    delete_related_plot_files(filename)
    delete_cleaned_version(filename)
