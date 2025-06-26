from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

from backend.utils.regression.session_state import (
    get_active_dataset,
    get_active_dataset_path,
    set_active_dataset
)
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.eda_utils import (
    dataset_overview,
    describe_data,
    generate_univariate_plots,
    generate_multivariate_plots,
    visualize_target_distribution,
)

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

# ─────────────────────────────────────────────
# GET: Render EDA Dashboard (Step 2)
# ─────────────────────────────────────────────
@router.get("/regression/eda", response_class=HTMLResponse)
async def eda_dashboard(request: Request):
    active_file = get_active_dataset()
    full_path = get_active_dataset_path()

    if not active_file or not os.path.exists(full_path):
        return templates.TemplateResponse("regression/eda_dashboard.html", {
            "request": request,
            "error": "❌ No active dataset selected or file missing.",
            "page": "eda",
            **get_sidebar_context(active_file=active_file, step=2),
        })

    df = pd.read_csv(full_path)
    overview = dataset_overview(df)

    return templates.TemplateResponse("regression/eda_dashboard.html", {
        "request": request,
        "overview": overview,
        "describe": None,
        "univariate": None,
        "multivariate": None,
        "columns": df.columns.tolist(),
        "filter_shape": None,
        "filtered_file": None,
        "page": "eda",
        **get_sidebar_context(active_file=active_file, step=2),
    })

# ─────────────────────────────────────────────
# POST: Perform EDA
# ─────────────────────────────────────────────
@router.post("/regression/eda", response_class=HTMLResponse)
async def describe_eda(request: Request):
    active_file = get_active_dataset()
    full_path = get_active_dataset_path()

    if not active_file or not os.path.exists(full_path):
        return templates.TemplateResponse("regression/eda_dashboard.html", {
            "request": request,
            "error": "❌ No active dataset selected or file missing.",
            "page": "eda",
            **get_sidebar_context(active_file=active_file, step=2),
        })

    df = pd.read_csv(full_path)
    overview = dataset_overview(df)
    desc_stats, missing_info = describe_data(df)

    univariate_plots = generate_univariate_plots(df, active_file)
    multivariate_plots = generate_multivariate_plots(df, active_file)

    return templates.TemplateResponse("regression/eda_dashboard.html", {
        "request": request,
        "overview": overview,
        "describe": {
            "summary": desc_stats.to_html(classes='table table-striped', border=0),
            "missing": missing_info.to_html(classes='table table-bordered', border=0),
        },
        "univariate": univariate_plots,
        "multivariate": multivariate_plots,
        "columns": df.columns.tolist(),
        "filter_shape": None,
        "filtered_file": None,
        "page": "eda",
        **get_sidebar_context(active_file=active_file, step=2),
    })

# ─────────────────────────────────────────────
# POST: Apply Target-Based Filtering
# ─────────────────────────────────────────────

@router.post("/regression/eda/filter", response_class=HTMLResponse)
async def apply_target_filter(
    request: Request,
    target_column: str = Form(...),
    lower_percentile: str = Form(...),
    upper_percentile: str = Form(...),
):
    active_file = get_active_dataset()
    full_path = get_active_dataset_path()

    if not active_file or not os.path.exists(full_path):
        return templates.TemplateResponse("regression/eda_dashboard.html", {
            "request": request,
            "error": "❌ No active dataset selected or file missing.",
            "page": "eda",
            **get_sidebar_context(active_file=active_file, step=2),
        })

    try:
        lower = float(lower_percentile)
        upper = float(upper_percentile)

        df = pd.read_csv(full_path)
        plot_path = visualize_target_distribution(df, target_column, lower, upper)

        return templates.TemplateResponse("regression/eda_dashboard.html", {
            "request": request,
            "overview": dataset_overview(df),
            "describe": None,
            "univariate": None,
            "multivariate": None,
            "columns": df.columns.tolist(),
            "filter_shape": None,
            "filtered_file": None,
            "target_dist_plot": plot_path,
            "page": "eda",
            **get_sidebar_context(active_file=active_file, step=2),
        })

    except Exception as e:
        return templates.TemplateResponse("regression/eda_dashboard.html", {
            "request": request,
            "error": f"❌ Filtering error: {str(e)}",
            "columns": pd.read_csv(full_path).columns.tolist(),
            "page": "eda",
            **get_sidebar_context(active_file=active_file, step=2),
        })
