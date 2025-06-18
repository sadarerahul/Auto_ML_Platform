from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page": "home"})

@router.get("/regression", response_class=HTMLResponse)
async def regression_workflow(request: Request):
    return templates.TemplateResponse("regression.html", {"request": request, "page": "regression"})
