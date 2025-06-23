from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression import feature_selection as fs
from backend.utils.regression.selection_state import load_xy, save_xy
from backend.services import dataset_service
from backend.config import MAX_DATASETS
from backend.utils.regression.session_state import get_active_dataset

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---------- GET ----------
@router.get("/regression/select_features", response_class=HTMLResponse)
async def select_features_page(request: Request):
    active = get_active_dataset()
    files = dataset_service.list_files()

    return templates.TemplateResponse(
        "regression/feature_selection.html",
        {
            "request": request,
            "page": "select_features",
            "numeric_columns": fs.numeric_columns(),
            "xy_state": load_xy(),
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )

# ---------- POST 1: correlation / top‑K ----------
@router.post("/regression/select_features", response_class=HTMLResponse)
async def run_feature_selection(
    request: Request,
    target_col: str = Form(...),
    top_k: int = Form(10),
):
    files = dataset_service.list_files()
    active = files[-1] if files else None
    try:
        series = fs.correlation_with_target(target_col)
        plot_html = fs.correlation_bar_html(series, f"Correlation vs {target_col}")
        selected = fs.top_features(series, int(top_k))
        message = f"✅ Top {top_k} features selected."
    except Exception as e:
        plot_html, selected = None, []
        message = f"❌ Error: {e}"

    return templates.TemplateResponse(
        "regression/feature_selection.html",
        {
            "request": request,
            "page": "select_features",
            "numeric_columns": fs.numeric_columns(),
            "plot_html": plot_html,
            "selected_features": selected,
            "target_col": target_col,
            "top_k": top_k,
            "xy_state": load_xy(),
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )

# ---------- POST 2: save X / y ----------
@router.post("/regression/select_features/xy", response_class=HTMLResponse)
async def save_xy_selection(
    request: Request,
    y_col: str = Form(...),
    x_cols: list[str] = Form(...),
):
    save_xy(x_cols, y_col)
    message = f"✅ Saved X ({len(x_cols)} columns) and y ({y_col})."

    files = dataset_service.list_files()
    active = files[-1] if files else None

    return templates.TemplateResponse(
        "regression/feature_selection.html",
        {
            "request": request,
            "page": "select_features",
            "numeric_columns": fs.numeric_columns(),
            "xy_state": load_xy(),
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )