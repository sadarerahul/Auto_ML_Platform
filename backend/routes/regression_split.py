from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression import train_test_split as tts
from backend.utils.regression.selection_state import load_xy
from backend.services import dataset_service
from backend.config import MAX_DATASETS

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---------- GET ----------
@router.get("/regression/split", response_class=HTMLResponse)
async def split_page(request: Request):
    files = dataset_service.list_files()
    active = files[-1] if files else None
    xy_state = load_xy()
    return templates.TemplateResponse(
        "regression/train_test_split.html",
        {
            "request": request,
            "page": "split",
            "xy_state": xy_state,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )

# ---------- POST ----------
@router.post("/regression/split", response_class=HTMLResponse)
async def do_split(
    request: Request,
    test_size_predefined: float = Form(None),
    test_size_manual: float = Form(None),
    random_state: int = Form(42),
):
    # Prioritize manual input if present
    test_size = test_size_manual if test_size_manual else test_size_predefined
    if test_size is None:
        test_size = 0.2  # default fallback

    files = dataset_service.list_files()
    active = files[-1] if files else None
    try:
        preview = tts.perform_split(test_size, random_state)
        message = f"✅ Split complete. Test size: {test_size}"
    except Exception as e:
        preview, message = None, f"❌ Error: {e}"

    return templates.TemplateResponse(
        "regression/train_test_split.html",
        {
            "request": request,
            "page": "split",
            "xy_state": load_xy(),
            "preview": preview,
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )