from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression import scale as scaler_utils
from backend.services import dataset_service
from backend.config import MAX_DATASETS

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---------- GET ----------
@router.get("/regression/scale", response_class=HTMLResponse)
async def scale_page(request: Request):
    files = dataset_service.list_files()
    active = files[-1] if files else None
    return templates.TemplateResponse(
        "regression/scale.html",
        {
            "request": request,
            "page": "scale",
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )

# ---------- POST ----------
@router.post("/regression/scale", response_class=HTMLResponse)
async def perform_scaling(
    request: Request,
    scaler_type: str = Form(...),   # 'standard' or 'minmax'
):
    files = dataset_service.list_files()
    active = files[-1] if files else None

    try:
        preview = scaler_utils.apply_scaler(scaler_type)
        message = f"✅ Scaling complete. Files saved as X_train_scaled.csv / X_test_scaled.csv."
    except Exception as e:
        preview = None
        message = f"❌ Error: {e}"

    return templates.TemplateResponse(
        "regression/scale.html",
        {
            "request": request,
            "page": "scale",
            "preview": preview,
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )