from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import pandas as pd
import os

from backend.utils.regression.eda_utils import (
    dataset_overview,
    describe_data,
    generate_univariate_plots,
    generate_multivariate_plots,
    filter_dataset_by_target
)

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")
UPLOAD_PATH = "frontend/static/uploads/recent.csv"

@router.get("/regression/eda", response_class=HTMLResponse)
async def eda_dashboard(request: Request):
    if not os.path.exists(UPLOAD_PATH):
        return templates.TemplateResponse("regression/eda_dashboard.html", {"request": request, "error": "No dataset found."})

    df = pd.read_csv(UPLOAD_PATH)
    overview = dataset_overview(df)
    return templates.TemplateResponse("regression/eda_dashboard.html", {
        "request": request,
        "overview": overview,
        "describe": None,
        "univariate": None,
        "multivariate": None,
        "columns": df.columns.tolist()
    })

@router.post("/regression/eda", response_class=HTMLResponse)
async def describe_eda(request: Request):
    if not os.path.exists(UPLOAD_PATH):
        return templates.TemplateResponse("regression/eda_dashboard.html", {"request": request, "error": "No dataset found."})

    df = pd.read_csv(UPLOAD_PATH)
    overview = dataset_overview(df)
    desc_stats, missing_info = describe_data(df)
    univariate_plots = generate_univariate_plots(df)
    multivariate_plots = generate_multivariate_plots(df)

    return templates.TemplateResponse("regression/eda_dashboard.html", {
        "request": request,
        "overview": overview,
        "describe": {
            "summary": desc_stats.to_html(classes='table table-striped', border=0),
            "missing": missing_info.to_html(classes='table table-bordered', border=0)
        },
        "univariate": univariate_plots,
        "multivariate": multivariate_plots,
        "columns": df.columns.tolist()
    })

@router.post("/regression/eda/filter", response_class=HTMLResponse)
async def apply_target_filter(
    request: Request,
    target_column: str = Form(...),
    lower_percentile: float = Form(...),
    upper_percentile: float = Form(...)
):
    if not os.path.exists(UPLOAD_PATH):
        return templates.TemplateResponse("regression/eda_dashboard.html", {"request": request, "error": "No dataset found."})

    try:
        # Convert 0-100% to 0-1.0 float
        q1 = lower_percentile / 100.0
        q3 = upper_percentile / 100.0

        df = pd.read_csv(UPLOAD_PATH)
        filtered_df, shape_str, filename = filter_dataset_by_target(df, target_column, q1, q3)

        # Overwrite the upload path
        filtered_df.to_csv(UPLOAD_PATH, index=False)

        overview = dataset_overview(filtered_df)

        return templates.TemplateResponse("regression/eda_dashboard.html", {
            "request": request,
            "overview": overview,
            "describe": None,
            "univariate": None,
            "multivariate": None,
            "columns": filtered_df.columns.tolist(),
            "filter_shape": shape_str,
            "filtered_file": filename
        })

    except Exception as e:
        return templates.TemplateResponse("regression/eda_dashboard.html", {
            "request": request,
            "error": f"Filtering error: {e}",
            "columns": pd.read_csv(UPLOAD_PATH).columns.tolist()
        })
