from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# Import logic from utils
from utils.upload import (
    save_uploaded_file,
    get_column_names,
    get_head_as_html,
    preview_uploaded_data
)
from utils.cleaning import (
    get_missing_columns,
    get_categorical_columns,
    apply_missing_value_strategy,
    apply_encoding,
    get_cleaned_data_preview
)

from utils.visualize import get_numeric_columns, generate_visualizations

# Initialize FastAPI app
app = FastAPI()

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../frontend/templates")
STATIC_DIR = os.path.join(BASE_DIR, "../frontend/static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Jinja and Static Mount
templates = Jinja2Templates(directory=TEMPLATE_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ------------------------
# 🌐 ROUTES
# ------------------------

# Homepage
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page": "home"})

# Regression Workflow Landing Page
@app.get("/regression", response_class=HTMLResponse)
async def regression_workflow(request: Request):
    return templates.TemplateResponse("regression.html", {"request": request, "page": "regression"})

# Regression Upload Page (GET)
@app.get("/regression/upload", response_class=HTMLResponse)
async def regression_upload_page(request: Request):
    return templates.TemplateResponse("regression/regression_upload.html", {
        "request": request,
        "page": "upload"
    })

# Handle Upload Form (POST)
@app.post("/regression/upload", response_class=HTMLResponse)
async def handle_upload(
    request: Request,
    file: UploadFile = File(...),
    file_type: str = Form(...)
):
    df, message = save_uploaded_file(file.file, file_type)
    if df is not None:
        return templates.TemplateResponse("regression/regression_upload.html", {
            "request": request,
            "page": "upload",
            "message": message,
            "columns": df.columns.tolist(),
        })
    else:
        return templates.TemplateResponse("regression/regression_upload.html", {
            "request": request,
            "page": "upload",
            "message": message
        })

# Handle Table Preview (Only Showing Table)
@app.post("/regression/preview", response_class=HTMLResponse)
async def preview_data(
    request: Request,
    action_type: str = Form(...),
    num_rows: int = Form(None)
):
    return await preview_uploaded_data(
        request=request,
        action_type=action_type,
        num_rows=num_rows
    )


# Data Cleaning
@app.get("/regression/clean", response_class=HTMLResponse)
async def clean_get(request: Request):
    return templates.TemplateResponse("regression/regression_clean.html", {
        "request": request,
        "page": "clean",
        "missing_columns": get_missing_columns(),
        "categorical_columns": get_categorical_columns(),
        "preview_table": get_cleaned_data_preview()
    })

# Handle Data Cleaning form POST
@app.post("/regression/clean", response_class=HTMLResponse)
async def clean_post(
    request: Request,
    cleaning_type: str = Form(...),
    column_name: str = Form(...),
    strategy: str = Form(...),
    custom_value: str = Form(None)
):
    message = ""
    success = False

    if cleaning_type == "missing":
        success, message = apply_missing_value_strategy(column_name, strategy, custom_value)
    elif cleaning_type == "encoding":
        success, message = apply_encoding(column_name, strategy)

    return templates.TemplateResponse("regression/regression_clean.html", {
        "request": request,
        "page": "clean",
        "message": message,
        "missing_columns": get_missing_columns(),
        "categorical_columns": get_categorical_columns(),
        "preview_table": get_cleaned_data_preview()
    })
    
# Visualization Route
@app.get("/regression/visualize", response_class=HTMLResponse)
async def show_visualization_ui(request: Request):
    numeric_cols = get_numeric_columns()
    return templates.TemplateResponse("regression/regression_visualize.html", {
        "request": request,
        "page": "visualize",
        "numeric_columns": numeric_cols
    })

# 📈 ROUTE: Visualization (POST)
@app.post("/regression/visualize", response_class=HTMLResponse)
async def handle_visualization_request(
    request: Request,
    selected_columns: list[str] = Form(...),              # Can select 1 or 2
    plot_types: list[str] = Form(...),                    # Can select multiple plots
    scatter_limit: int = Form(default=100)                # Optional limit
):
    numeric_cols = get_numeric_columns()

    # 🧠 Generate plots based on logic in visualize.py
    plots = generate_visualizations(
        selected_columns=selected_columns,
        plot_types=plot_types,
        scatter_limit=scatter_limit
    )

    return templates.TemplateResponse("regression/regression_visualize.html", {
        "request": request,
        "page": "visualize",
        "numeric_columns": numeric_cols,
        "plots": plots
    })