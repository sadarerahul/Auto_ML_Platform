from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os


from ..utils.regression.visualize import get_numeric_columns, generate_visualizations

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@router.get("/regression/visualize", response_class=HTMLResponse)
async def visualize_get(request: Request):
    return templates.TemplateResponse(
        "regression/regression_visualize.html",
        {"request": request, "page": "visualize", "numeric_columns": get_numeric_columns()}
    )

@router.post("/regression/visualize", response_class=HTMLResponse)
async def visualize_post(request: Request,
                         selected_columns: list[str] = Form(...),
                         plot_types: list[str] = Form(...),
                         scatter_limit: int = Form(100)):
    plots = generate_visualizations(selected_columns, plot_types, scatter_limit)
    return templates.TemplateResponse(
        "regression/regression_visualize.html",
        {
            "request": request,
            "page": "visualize",
            "numeric_columns": get_numeric_columns(),
            "plots": plots
        }
    )
