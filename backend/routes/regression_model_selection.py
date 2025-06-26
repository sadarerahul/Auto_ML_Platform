from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
import pandas as pd

from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.model_selection import available_models, train_and_evaluate
from backend.utils.regression.session_state import get_active_dataset
from backend.services import dataset_service
from backend.config import MAX_DATASETS

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# ── GET: Model selection page ──────────────────────────────
@router.get("/regression/model", response_class=HTMLResponse)
async def model_page(request: Request):
    active = get_active_dataset()
    files = dataset_service.list_files()

    return templates.TemplateResponse(
        "regression/model_selection.html",
        {
            "request": request,
            "page": "model",
            "models": available_models(),
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )


# ── POST: Train selected models ─────────────────────────────
@router.post("/regression/model", response_class=HTMLResponse)
async def train_models(
    request: Request,
    selected_models: Optional[list[str]] = Form(None),
):
    active = get_active_dataset()
    files = dataset_service.list_files()

    if not selected_models:
        message = "⚠️ Please select at least one model to train."
        return templates.TemplateResponse(
            "regression/model_selection.html",
            {
                "request": request,
                "page": "model",
                "models": available_models(),
                "message": message,
                "files": files,
                "active_file": active,
                "max_datasets": MAX_DATASETS,
                **get_sidebar_context(active_file=active),
            },
        )

    try:
        results_df = train_and_evaluate(selected_models, dataset_name=active)
        table_html = results_df.to_html(classes="table table-dark table-sm", index=False)
        message = "✅ Training finished. Models saved in static/models/ with dataset-linked names."
    except Exception as e:
        table_html, message = None, f"❌ Error during training: {e}"

    return templates.TemplateResponse(
        "regression/model_selection.html",
        {
            "request": request,
            "page": "model",
            "models": available_models(),
            "selected": selected_models,
            "results_table": table_html,
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )