from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import re
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from backend.utils.regression.outliers import get_numeric_columns_for_outliers

from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression.smoothing import (
    lowess_smooth, median_filter, hampel_filter
)
from backend.utils.regression.session_state import get_active_dataset

router = APIRouter(prefix="/regression")
templates = Jinja2Templates(directory="frontend/templates")

UPLOAD_DIR = Path("frontend/static/uploads")
PROCESSED_DIR = Path("frontend/static/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

smoothing_runs: list[dict] = []


def get_active_csv_path() -> Path:
    name = get_active_dataset()
    if not name:
        raise HTTPException(404, "⚠️ No active dataset selected.")
    path = UPLOAD_DIR / name
    if not path.exists():
        raise HTTPException(404, f"Dataset '{name}' not found.")
    return path


def safe_name(text: str) -> str:
    """Replace unsafe characters for filenames."""
    return re.sub(r"[^\w\-.]", "_", text)


@router.get("/smooth", response_class=HTMLResponse)
def smooth_page(request: Request):
    path = get_active_csv_path()
    df_sample = pd.read_csv(path, nrows=5)
    num_cols = get_numeric_columns_for_outliers()

    return templates.TemplateResponse(
        "regression/smooth.html",
        {
            "request": request,
            "page": "smooth",
            "dataset_name": path.name,
            "columns": num_cols,
            **get_sidebar_context(active_file=path.name),
        },
    )


@router.post("/smooth/preview")
def preview(column: str = Form(...)):
    path = get_active_csv_path()
    df = pd.read_csv(path, usecols=[column])

    global smoothing_runs
    smoothing_runs.clear()

    return {
        "x": list(range(len(df))),
        "y_raw": df[column].replace({np.nan: None}).tolist(),
        "lines": [],
    }


@router.post("/smooth/apply")
def apply_smoothing(
    column: str = Form(...),
    method: str = Form(...),
    frac: float = Form(0.1),
    kernel: int = Form(5),
    window: int = Form(7),
    n_sigmas: float = Form(3.0),
    clear: bool = Form(False)
):
    path = get_active_csv_path()
    df = pd.read_csv(path)

    if column not in df.columns:
        raise HTTPException(400, "Selected column not found.")

    # Apply smoothing
    if method == "lowess":
        smoothed = lowess_smooth(df[column], frac=frac)
        label = f"LOWESS (frac={frac})"
    elif method == "median":
        smoothed = median_filter(df[column], kernel=kernel)
        label = f"Median (k={kernel})"
    elif method == "hampel":
        smoothed = hampel_filter(df[column], window=window, n_sigmas=n_sigmas)
        label = f"Hampel (w={window}, σ={n_sigmas})"
    else:
        raise HTTPException(400, "Invalid smoothing method.")

    # Save result with safe name
    new_col = f"{column}_{method}"
    df[new_col] = smoothed
    out_name = f"{safe_name(path.stem)}_{safe_name(column)}_{safe_name(method)}.csv"
    out_fp = PROCESSED_DIR / out_name
    df.to_csv(out_fp, index=False)

    global smoothing_runs
    if clear:
        smoothing_runs.clear()
    smoothing_runs.append({
        "label": label,
        "y": smoothed.replace({np.nan: None}).tolist(),
    })

    return {
        "x": list(range(len(df))),
        "y_raw": df[column].replace({np.nan: None}).tolist(),
        "lines": smoothing_runs,
        "out_file": out_name,
    }


@router.get("/smooth/download/{fname}")
def download_result(fname: str):
    path = PROCESSED_DIR / fname
    if not path.exists():
        raise HTTPException(404, "File not found.")
    return FileResponse(path, media_type="text/csv", filename=fname)