from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from backend.utils.regression.context import get_sidebar_context
from ..utils.regression.session_state import get_active_dataset
from ..utils.regression.cleaning import (
    get_missing_columns, get_categorical_columns,
    apply_missing_value_strategy, apply_encoding,
    get_cleaned_data_preview
)

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---------- GET: Cleaning Page ----------
@router.get("/regression/clean", response_class=HTMLResponse)
async def clean_get(request: Request):
    filename = get_active_dataset()
    if not filename:
        return templates.TemplateResponse("regression/regression_clean.html", {
            "request": request,
            "page": "clean",
            "message": "⚠️ No active dataset selected.",
            "message_type": "warning",
            "missing_columns": [],
            "categorical_columns": [],
            "preview_table": "<p class='text-warning'>No dataset loaded.</p>",
            
        })

    context = {
        "request": request,
        "page": "clean",
        "missing_columns": get_missing_columns(),
        "categorical_columns": get_categorical_columns(),
        "preview_table": get_cleaned_data_preview(),
        **get_sidebar_context(active_file=filename)
    }
    return templates.TemplateResponse("regression/regression_clean.html", context)

# ---------- POST: Apply Cleaning or Encoding ----------
@router.post("/regression/clean", response_class=HTMLResponse)
async def clean_post(request: Request,
                     cleaning_type: str = Form(...),
                     column_name: str = Form(...),
                     strategy: str = Form(...),
                     custom_value: str | None = Form(None)):

    if cleaning_type == "missing":
        success, msg = apply_missing_value_strategy(column_name, strategy, custom_value)
    else:
        success, msg = apply_encoding(column_name, strategy)

    filename = get_active_dataset()
    if not filename:
        success = False
        msg = "⚠️ No active dataset selected."

    context = {
        "request": request,
        "page": "clean",
        "message": msg,
        "message_type": "success" if success else "danger",
        "missing_columns": get_missing_columns(),
        "categorical_columns": get_categorical_columns(),
        "preview_table": get_cleaned_data_preview(),
        **get_sidebar_context(active_file=filename)
    }
    return templates.TemplateResponse("regression/regression_clean.html", context)