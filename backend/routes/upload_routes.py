from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.upload import get_column_names, get_head_as_html, save_uploaded_file
from backend.utils.regression.session_state import get_active_dataset
from backend.services import dataset_service  # in case you still need delete_files

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---------- GET: Upload Page ----------
@router.get("/regression/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    filename = get_active_dataset()
    cols = get_column_names() if filename else []
    preview = get_head_as_html(10) if cols else None

    context = {
        "request": request,
        "page": "upload",
        "columns": cols,
        "preview_table": preview,
        **get_sidebar_context(active_file=filename)
    }
    return templates.TemplateResponse("regression/regression_upload.html", context)

# ---------- POST: Upload File ----------
@router.post("/regression/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    df, msg = await save_uploaded_file(file)

    if df is not None:
        preview = df.head(10).to_html(classes="table table-striped table-bordered", index=False)
        cols = df.columns.tolist()
        active_file = file.filename
    else:
        preview = None
        cols = []
        active_file = ""

    context = {
        "request": request,
        "page": "upload",
        "message": msg,
        "columns": cols,
        "preview_table": preview,
        **get_sidebar_context(active_file=active_file)
    }
    return templates.TemplateResponse("regression/regression_upload.html", context)

# ---------- POST: Delete Datasets ----------
@router.post("/regression/delete", response_class=HTMLResponse)
async def delete_datasets(request: Request, filenames: list[str] = File(...)):
    dataset_service.delete_files(filenames)
    return await upload_page(request)