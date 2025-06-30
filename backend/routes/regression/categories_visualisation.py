from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import pandas as pd
import os
from backend.utils.regression.categories_visualisation_utils import load_data 


from backend.utils.regression.categories_visualisation_utils import generate_comparison_histograms
from backend.utils.regression.session_state import get_active_dataset_path, get_active_dataset
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.outliers import get_numeric_columns_for_outliers

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/regression/categories", response_class=HTMLResponse)
async def category_visualisation_get(request: Request):
    dataset_path = get_active_dataset_path()
    if not dataset_path or not os.path.exists(dataset_path):
        return templates.TemplateResponse("regression/categories_visualisation.html", {
            "request": request, "error": "No dataset found."
        })

    df = load_data()
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    all_columns = df.columns.tolist()
    active_file = get_active_dataset()

    return templates.TemplateResponse("regression/categories_visualisation.html", {
        "request": request,
        "columns": all_columns,
        "numeric_columns": numeric_cols,
        **get_sidebar_context(active_file=active_file, step=2),
    })

@router.post("/regression/categories", response_class=HTMLResponse)
async def category_visualisation_post(
    request: Request,
    target_column: str = Form(...),
    selected_features: List[str] = Form(...),
    lower_percentile: float = Form(25),
    upper_percentile: float = Form(75)
):
    dataset_path = get_active_dataset_path()
    if not dataset_path or not os.path.exists(dataset_path):
        return templates.TemplateResponse("regression/categories_visualisation.html", {
            "request": request, "error": "No dataset found."
        })

    df = load_data()
    active_file = get_active_dataset()

    try:
        plots = generate_comparison_histograms(df, target_column, selected_features, lower_percentile, upper_percentile)
        return templates.TemplateResponse("regression/categories_visualisation.html", {
            "request": request,
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include='number').columns.tolist(),
            "plots": plots,
            "success": f"{len(plots)} plot(s) generated successfully.",
            **get_sidebar_context(active_file=active_file, step=2),
        })
    except Exception as e:
        return templates.TemplateResponse("regression/categories_visualisation.html", {
            "request": request,
            "error": str(e),
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include='number').columns.tolist(),
            **get_sidebar_context(active_file=active_file, step=2),
        })
