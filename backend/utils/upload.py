import os
import uuid
import pandas as pd
from fastapi import Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .paths import DATA_PATH

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "../../frontend/static/uploads")
TEMPLATE_DIR = os.path.join(BASE_DIR, "../../frontend/templates")
DATA_PATH = os.path.join(UPLOAD_DIR, "uploaded_data.csv")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATE_DIR)

def list_saved_datasets() -> list[str]:
    """Return all user‑saved dataset filenames (exclude canonical copy)."""
    return [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv") and f != "uploaded_data.csv"
    ]

def delete_saved_dataset(filename: str) -> bool:
    """Remove a dataset file; True if removed."""
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

# --------------------------------------------
# ✅ Save the uploaded file and return DataFrame
# --------------------------------------------
def save_uploaded_file(file, file_type="csv", original_name: str | None = None):
    """
    Read the uploaded file into a DataFrame, save a unique CSV copy
    in uploads folder, and overwrite canonical DATA_PATH.
    """
    try:
        # -------- read to DataFrame --------
        if file_type == "csv":
            df = pd.read_csv(file)
        elif file_type == "excel":
            df = pd.read_excel(file, engine="openpyxl")
        else:
            raise ValueError("Unsupported file format")

        # -------- save canonical -----------
        df.to_csv(DATA_PATH, index=False)

        # -------- save unique copy ---------
        safe_original = (original_name or "dataset").replace(" ", "_")
        unique_name   = f"{uuid.uuid4().hex}_{os.path.splitext(safe_original)[0]}.csv"
        df.to_csv(os.path.join(UPLOAD_DIR, unique_name), index=False)

        return df, "✅ File uploaded successfully!"
    except Exception as exc:
        return None, f"❌ Error: {exc}"

# --------------------------------------------
# ✅ Return column names from uploaded file
# --------------------------------------------
def get_column_names():
    try:
        return pd.read_csv(DATA_PATH).columns.tolist()
    except Exception:
        return []

# --------------------------------------------
# ✅ Return df.head(n) as HTML
# --------------------------------------------
def get_head_as_html(n=10):
    try:
        return (
            pd.read_csv(DATA_PATH)
            .head(n)
            .to_html(classes="table table-striped table-bordered", index=False)
        )
    except Exception as exc:
        return f"<p class='text-danger'>❌ Failed to load preview: {exc}</p>"

async def preview_uploaded_data(request: Request,
                                action_type: str = Form(...),
                                num_rows: int = Form(None)):
    columns = get_column_names()
    preview_table = None
    message = None

    if action_type == "show_table" and num_rows:
        preview_table = get_head_as_html(num_rows)
        message = f"✅ Showing top {num_rows} rows"

    return templates.TemplateResponse(
        "regression/regression_upload.html",
        {
            "request": request,
            "page": "upload",
            "columns": columns,
            "preview_table": preview_table,
            "message": message,
            "datasets": list_saved_datasets(),   # show file list
            "show_delete": False                 # default
        }
    )