from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from typing import Optional

from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression import train_test_split as tts
from backend.utils.regression.selection_state import load_xy
from backend.services import dataset_service
from backend.config import MAX_DATASETS

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

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

@router.post("/regression/split", response_class=HTMLResponse)
async def do_split(
    request: Request,
    split_method: str = Form("random"),
    test_size_predefined: Optional[str] = Form(None),
    test_size_manual: Optional[str] = Form(None),
    seq_test_size_predefined: Optional[str] = Form(None),
    seq_test_size_manual: Optional[str] = Form(None),
    random_state: int = Form(42)
):
    files = dataset_service.list_files()
    active = files[-1] if files else None
    xy_state = load_xy()

    try:
        if split_method == "random":
            test_size = 0.2
            if test_size_manual and test_size_manual.strip():
                test_size = float(test_size_manual)
            elif test_size_predefined and test_size_predefined.strip():
                test_size = float(test_size_predefined)

            preview = tts.perform_split(
                test_size=test_size,
                random_state=random_state,
                preview_rows=5
            )
            message = f"✅ Random split complete — Test size: {test_size}"

        elif split_method == "seq":
            test_size = 0.2
            if seq_test_size_manual and seq_test_size_manual.strip():
                test_size = float(seq_test_size_manual)
            elif seq_test_size_predefined and seq_test_size_predefined.strip():
                test_size = float(seq_test_size_predefined)

            preview = tts.perform_sequential_split(
                test_size=test_size,
                preview_rows=5
            )
            message = f"✅ Sequential split complete — Test size: {test_size}"

        else:
            raise ValueError("Invalid split method selected.")

    except Exception as e:
        preview, message = None, f"❌ Error: {e}"

    return templates.TemplateResponse(
        "regression/train_test_split.html",
        {
            "request": request,
            "page": "split",
            "xy_state": xy_state,
            "preview": preview,
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            "split_method": split_method,
            **get_sidebar_context(active_file=active),
        },
    )
