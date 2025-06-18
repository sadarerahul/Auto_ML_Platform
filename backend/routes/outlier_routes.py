from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os


from ..utils.regression.outliers import get_numeric_columns_for_outliers, handle_outliers

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@router.get("/regression/outliers", response_class=HTMLResponse)
async def outlier_get(request: Request):
    return templates.TemplateResponse(
        "regression/regression_outliers.html",
        {
            "request": request,
            "page": "outliers",
            "numeric_columns": get_numeric_columns_for_outliers()
        }
    )

@router.post("/regression/outliers", response_class=HTMLResponse)
async def outlier_post(request: Request,
                       column_name: str = Form(...),
                       method: str = Form(...)):
    before, after, msg = handle_outliers(column_name, method)
    return templates.TemplateResponse(
        "regression/regression_outliers.html",
        {
            "request": request,
            "page": "outliers",
            "numeric_columns": get_numeric_columns_for_outliers(),
            "message": msg,
            "summary_before": before,
            "summary_after": after
        }
    )
