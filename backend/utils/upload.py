import os
import pandas as pd
from fastapi import Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "../../frontend/static/uploads")
TEMPLATE_DIR = os.path.join(BASE_DIR, "../../frontend/templates")
DATA_PATH = os.path.join(UPLOAD_DIR, "uploaded_data.csv")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# --------------------------------------------
# ✅ Save the uploaded file and return DataFrame
# --------------------------------------------
def save_uploaded_file(file, file_type="csv"):
    try:
        if file_type == "csv":
            df = pd.read_csv(file)
        elif file_type == "excel":
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format")

        df.to_csv(DATA_PATH, index=False)  # Standardize save as CSV
        return df, "✅ File uploaded successfully!"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# --------------------------------------------
# ✅ Return column names from uploaded file
# --------------------------------------------
def get_column_names():
    try:
        df = pd.read_csv(DATA_PATH)
        return df.columns.tolist()
    except Exception:
        return []

# --------------------------------------------
# ✅ Return df.head(n) as HTML
# --------------------------------------------
def get_head_as_html(n=10):
    try:
        df = pd.read_csv(DATA_PATH)
        return df.head(n).to_html(classes="table table-striped table-bordered", index=False)
    except Exception as e:
        return f"<p class='text-danger'>❌ Failed to load preview: {str(e)}</p>"

# --------------------------------------------
# ✅ Handler for previewing table (POST /regression/preview)
# --------------------------------------------
async def preview_uploaded_data(
    request: Request,
    action_type: str = Form(...),
    num_rows: int = Form(None)
) -> HTMLResponse:
    try:
        columns = get_column_names()
        preview_table = None
        message = None

        if action_type == "show_table" and num_rows:
            preview_table = get_head_as_html(num_rows)
            message = f"✅ Showing top {num_rows} rows"

        return templates.TemplateResponse("regression/regression_upload.html", {
            "request": request,
            "columns": columns,
            "preview_table": preview_table,
            "message": message
        })

    except Exception as e:
        return templates.TemplateResponse("regression/regression_upload.html", {
            "request": request,
            "message": f"❌ Preview failed: {str(e)}"
        })
