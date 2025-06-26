from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from typing import Optional

from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.session_state import get_active_dataset
from backend.utils.regression.cleaning import (
    get_missing_columns,
    get_categorical_columns,
    apply_missing_value_strategy,
    apply_encoding,
    get_cleaned_data_preview,
)

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

STEP_ID = 3  # ← Pre-processing / Cleaning step

# ──────────────────────────────────────────────
# GET  /regression/clean
# ──────────────────────────────────────────────
@router.get("/regression/clean", response_class=HTMLResponse)
async def clean_get(request: Request):
    filename = get_active_dataset()

    if not filename:
        return templates.TemplateResponse(
            "regression/regression_clean.html",
            {
                "request": request,
                "page": "clean",
                "message": "⚠️ No active dataset selected.",
                "message_type": "warning",
                "missing_columns": [],
                "categorical_columns": [],
                "preview_table": "<p class='text-warning mb-0'>No dataset loaded.</p>",
                **get_sidebar_context(step=STEP_ID),
            },
        )

    context = {
        "request": request,
        "page": "clean",
        "missing_columns": get_missing_columns(),
        "categorical_columns": get_categorical_columns(),
        "preview_table": get_cleaned_data_preview(),
        **get_sidebar_context(active_file=filename, step=STEP_ID),
    }
    return templates.TemplateResponse("regression/regression_clean.html", context)

# ──────────────────────────────────────────────
# POST  /regression/clean
# ──────────────────────────────────────────────
@router.post("/regression/clean", response_class=HTMLResponse)
async def clean_post(
    request: Request,
    cleaning_type: str = Form(...),      # "missing" or "encoding"
    column_name: str = Form(...),
    strategy: str = Form(...),           # e.g., "mean", "drop", "onehot", etc.
    custom_value: Optional[str] = Form(None),
):
    filename = get_active_dataset()
    if not filename:
        success, msg = False, "⚠️ No active dataset selected."
    else:
        # ── Handle missing-value operations
        if cleaning_type == "missing":
            # Try casting custom value to number if applicable
            if strategy == "custom" and custom_value is not None:
                try:
                    custom_value_cast = float(custom_value)
                except ValueError:
                    custom_value_cast = custom_value
            else:
                custom_value_cast = None

            success, msg = apply_missing_value_strategy(
                column_name, strategy, custom_value_cast
            )

        # ── Handle encoding operations
        elif cleaning_type == "encoding":
            success, msg = apply_encoding(column_name, strategy)
        else:
            success, msg = False, "❌ Invalid cleaning type."

    # 🔁 Updated context after cleaning
    updated_filename = get_active_dataset()  # may have changed to _cleaned
    context = {
        "request": request,
        "page": "clean",
        "message": msg,
        "message_type": "success" if success else "danger",
        "missing_columns": get_missing_columns(),
        "categorical_columns": get_categorical_columns(),
        "preview_table": get_cleaned_data_preview(),
        **get_sidebar_context(active_file=updated_filename, step=STEP_ID),
    }
    return templates.TemplateResponse("regression/regression_clean.html", context)
