from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.visualize import get_numeric_columns, generate_visualizations
from backend.utils.regression.session_state import get_active_dataset
from backend.utils.regression.visualize_state import (
    get_visualize_results,
    update_visualize_results,
)

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

STEP_ID = 4  # Visualization step

# ─────────────────────────────────────────────
# GET: Render Visualization Page
# ─────────────────────────────────────────────
@router.get("/regression/visualize", response_class=HTMLResponse)
async def visualize_get(request: Request):
    active_file = get_active_dataset()
    numeric_cols = get_numeric_columns()

    # Load previous visualization state
    saved = get_visualize_results(active_file) if active_file else None
    x_column = saved.get("x_column") if saved else None
    y_column = saved.get("y_column") if saved else None
    plot_types = saved.get("plot_types") if saved else []
    scatter_limit = saved.get("scatter_limit") if saved else 100
    plots = saved.get("plots") if saved else []

    return templates.TemplateResponse("regression/regression_visualize.html", {
        "request": request,
        "page": "visualize",
        "numeric_columns": numeric_cols,
        "x_column": x_column,
        "y_column": y_column,
        "plot_types": plot_types,
        "scatter_limit": scatter_limit,
        "plots": plots,
        **get_sidebar_context(active_file=active_file, step=STEP_ID)
    })


# ─────────────────────────────────────────────
# POST: Generate Visualizations
# ─────────────────────────────────────────────
@router.post("/regression/visualize", response_class=HTMLResponse)
async def visualize_post(
    request: Request,
    x_column: str = Form(...),
    y_column: str = Form(""),
    plot_types: list[str] = Form(...),
    scatter_limit: int = Form(100)
):
    active_file = get_active_dataset()
    plots = generate_visualizations(x_column, y_column, plot_types, scatter_limit)

    # Save state for persistence
    update_visualize_results(active_file, "x_column", x_column)
    update_visualize_results(active_file, "y_column", y_column)
    update_visualize_results(active_file, "plot_types", plot_types)
    update_visualize_results(active_file, "scatter_limit", scatter_limit)
    update_visualize_results(active_file, "plots", plots)

    return templates.TemplateResponse("regression/regression_visualize.html", {
        "request": request,
        "page": "visualize",
        "numeric_columns": get_numeric_columns(),
        "x_column": x_column,
        "y_column": y_column,
        "plot_types": plot_types,
        "scatter_limit": scatter_limit,
        "plots": plots,
        "message": f"✅ Generated {len(plots)} plot(s) based on your selection.",
        "message_type": "success",
        **get_sidebar_context(active_file=active_file, step=STEP_ID)
    })
