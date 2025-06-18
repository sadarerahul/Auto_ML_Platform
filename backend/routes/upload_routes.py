from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from backend.utils.regression.context import get_sidebar_context

from ..utils.regression.upload import (
    get_column_names,
    get_head_as_html,
    preview_uploaded_data
)
from ..services import dataset_service
from backend.config import MAX_DATASETS    

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---------- GET: upload page ----------
# ---------- GET: upload page ----------
@router.get("/regression/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    cols = get_column_names()
    preview = get_head_as_html(10) if cols else None

    upload_dir = "frontend/static/uploads"
    files = sorted(
        os.listdir(upload_dir),
        key=lambda f: os.path.getmtime(os.path.join(upload_dir, f)),
        reverse=True
    )
    active = files[0] if files else None

    return templates.TemplateResponse(
        "regression/regression_upload.html",
        {
            "request": request,
            "page": "upload",
            "columns": cols,
            "preview_table": preview,
            "files": files,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active)
        }
    )

# ---------- POST: upload file ----------
@router.post("/regression/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    df, msg, blocked = dataset_service.upload_dataset(file)
    cols = df.columns.tolist() if df is not None else get_column_names()

    upload_dir = "frontend/static/uploads"
    files = sorted(
        os.listdir(upload_dir),
        key=lambda f: os.path.getmtime(os.path.join(upload_dir, f)),
        reverse=True
    )
    active = files[0] if files else None

    return templates.TemplateResponse(
        "regression/regression_upload.html",
        {
            "request": request,
            "page": "upload",
            "message": msg,
            "columns": cols,
            "files": files,
            "max_datasets": MAX_DATASETS,
            "show_delete": blocked,
            **get_sidebar_context(active_file=active)
        }
    )


# ---------- POST: preview table ----------
@router.post("/regression/preview", response_class=HTMLResponse)
async def preview_table(request: Request,
                        action_type: str = Form(...),
                        num_rows: int = Form(None)):
    return await preview_uploaded_data(request, action_type, num_rows)

# ---------- POST: delete ----------
@router.post("/regression/delete", response_class=HTMLResponse)
async def delete_datasets(request: Request, filenames: list[str] = Form(...)):
    dataset_service.delete_files(filenames)
    return await upload_page(request)  # 🟡 It will recompute active_file from scratch
