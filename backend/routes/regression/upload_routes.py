from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import pandas as pd

from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.upload import (
    get_column_names,
    get_head_as_html,
    save_uploaded_file,
    clear_all_cache_for,
)
from backend.utils.regression.session_state import (
    get_active_dataset,
    clear_active_dataset,
    set_active_dataset,
)
from backend.services import dataset_service

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
CLEANED_DIR = os.path.abspath("frontend/static/cleaned")

# ──────────────────────────────────────────────
# GET: Upload Page
# ──────────────────────────────────────────────
@router.get("/regression/upload", response_class=HTMLResponse, name="upload_page")
async def upload_page(request: Request):
    active_file = get_active_dataset()
    cols = get_column_names() if active_file else []
    preview = get_head_as_html(10) if active_file else None

    context = {
        "request": request,
        "page": "upload",
        "columns": cols,
        "preview_table": preview,
        **get_sidebar_context(active_file=active_file),
    }
    return templates.TemplateResponse("regression/regression_upload.html", context)

# ──────────────────────────────────────────────
# POST: Upload Dataset File
# ──────────────────────────────────────────────
@router.post("/regression/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    df, msg = await save_uploaded_file(file)

    if df is not None:
        preview = df.head(10).to_html(classes="table table-striped table-bordered", index=False)
        cols = df.columns.tolist()
        raw_name = os.path.basename(file.filename)

        # ✅ Save cleaned version in cleaned/ folder
        cleaned_name = raw_name.replace(".csv", "_cleaned.csv")
        cleaned_path = os.path.join(CLEANED_DIR, cleaned_name)
        df.to_csv(cleaned_path, index=False)

        # ✅ Keep original dataset as active
        set_active_dataset(raw_name)
    else:
        preview, cols, raw_name = None, [], ""

    context = {
        "request": request,
        "page": "upload",
        "message": msg,
        "columns": cols,
        "preview_table": preview,
        **get_sidebar_context(active_file=raw_name),
    }
    return templates.TemplateResponse("regression/regression_upload.html", context)

# ──────────────────────────────────────────────
# POST: Delete Selected Datasets
# ──────────────────────────────────────────────
@router.post("/regression/delete")
async def delete_datasets(request: Request, filenames: list[str] = Form(...)):
    active_file = get_active_dataset()

    for fname in filenames:
        clear_all_cache_for(fname)  # ✅ Clear all associated files

    dataset_service.delete_files(filenames)

    # If active dataset was deleted, reset it
    if active_file in filenames:
        clear_active_dataset()

    return RedirectResponse(url=router.url_path_for("upload_page"), status_code=303)
