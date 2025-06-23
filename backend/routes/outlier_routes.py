from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from backend.utils.regression.context import get_sidebar_context
from ..utils.regression.session_state import get_active_dataset
from ..utils.regression.outliers import (
    get_numeric_columns_for_outliers,
    handle_outliers,
    generate_outlier_plot
)

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---------- GET ----------
@router.get("/regression/outliers", response_class=HTMLResponse)
async def outlier_get(request: Request):
    filename = get_active_dataset()
    if not filename:
        return templates.TemplateResponse("regression/regression_outliers.html", {
            "request": request,
            "page": "outliers",
            "numeric_columns": [],
            "message": "⚠️ No active dataset selected.",
            "message_type": "warning",
            **get_sidebar_context(active_file=None)
        })

    numeric_columns = get_numeric_columns_for_outliers()
    return templates.TemplateResponse("regression/regression_outliers.html", {
        "request": request,
        "page": "outliers",
        "numeric_columns": numeric_columns,
        **get_sidebar_context(active_file=filename)
    })

# ---------- POST: Step 1 (Visualize Column) ----------
@router.post("/regression/outliers/visualize", response_class=HTMLResponse)
async def outlier_visualize(request: Request, column_name: str = Form(...)):
    filename = get_active_dataset()
    numeric_columns = get_numeric_columns_for_outliers()
    plot_html, suggestion = generate_outlier_plot(column_name)

    return templates.TemplateResponse("regression/regression_outliers.html", {
        "request": request,
        "page": "outliers",
        "numeric_columns": numeric_columns,
        "selected_column": column_name,
        "plot_html": plot_html,
        "suggested_method": suggestion,
        **get_sidebar_context(active_file=filename)
    })

# ---------- POST: Step 2 (Apply Cleaning) ----------
@router.post("/regression/outliers/apply", response_class=HTMLResponse)
async def outlier_clean(request: Request,
                        column_name: str = Form(...),
                        method: str = Form(...)):
    filename = get_active_dataset()
    before, after, msg = handle_outliers(column_name, method)
    success = before is not None and after is not None
    numeric_columns = get_numeric_columns_for_outliers()
    plot_html, suggestion = generate_outlier_plot(column_name)

    return templates.TemplateResponse("regression/regression_outliers.html", {
        "request": request,
        "page": "outliers",
        "numeric_columns": numeric_columns,
        "selected_column": column_name,
        "plot_html": plot_html,
        "suggested_method": suggestion,
        "summary_before": before,
        "summary_after": after,
        "message": msg,
        "message_type": "success" if success else "danger",
        **get_sidebar_context(active_file=filename)
    })