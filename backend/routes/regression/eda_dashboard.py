from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

from backend.utils.regression.eda_state import (
    get_eda_results, update_eda_results
)
from backend.utils.regression.session_state import (
    get_active_dataset,
    get_active_dataset_path
)
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.eda_utils import (
    dataset_overview,
    describe_data,
    generate_univariate_plots,
    generate_multivariate_plots
)

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


# ─────────────────────────────────────────────
# GET: Render EDA Dashboard (with previous state if available)
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

    # Load previous EDA results if available
    saved = get_eda_results(active_file) or {}
    describe = saved.get("describe")
    univariate = saved.get("univariate")
    multivariate = saved.get("multivariate")

    return templates.TemplateResponse("regression/eda_dashboard.html", {
        "request": request,
        "overview": overview,
        "describe": describe,
        "univariate": univariate,
        "multivariate": multivariate,
        "columns": df.columns.tolist(),
        "page": "eda",
        **get_sidebar_context(active_file=active_file, step=2),
    })


# ─────────────────────────────────────────────
# POST: Perform EDA & Save State
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

    # Convert DataFrames to HTML tables
    describe_html = {
        "summary": desc_stats.to_html(classes="table table-striped", border=0),
        "missing": missing_info.to_html(classes="table table-bordered", border=0),
    }

    # Generate plots
    univariate_plots = generate_univariate_plots(df, active_file)
    multivariate_plots = generate_multivariate_plots(df, active_file)

    # Save state for future visits
    update_eda_results(active_file, "describe", describe_html)
    update_eda_results(active_file, "univariate", univariate_plots)
    update_eda_results(active_file, "multivariate", multivariate_plots)

    return templates.TemplateResponse("regression/eda_dashboard.html", {
        "request": request,
        "overview": overview,
        "describe": describe_html,
        "univariate": univariate_plots,
        "multivariate": multivariate_plots,
        "columns": df.columns.tolist(),
        "page": "eda",
        **get_sidebar_context(active_file=active_file, step=2),
    })
