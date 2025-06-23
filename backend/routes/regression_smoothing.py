from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse

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


def get_active_csv_path() -> Path:
    """Resolve active dataset path (in uploads)."""
    active_name = get_active_dataset()
    if not active_name:
        raise HTTPException(404, "⚠️ No active dataset selected.")
    path = UPLOAD_DIR / active_name
    if not path.exists():
        raise HTTPException(404, f"Dataset '{active_name}' not found.")
    return path


# ── 1️⃣ main smoothing page ─────────────────────────────────
@router.get("/smooth", response_class=HTMLResponse)
def smooth_page(request: Request):
    ds_path = get_active_csv_path()
    df_sample = pd.read_csv(ds_path, nrows=5)
    numeric_cols = df_sample.select_dtypes("number").columns.tolist()

    return templates.TemplateResponse(
        "regression/smooth.html",
        {
            "request": request,
            "dataset_name": ds_path.name,
            "columns": numeric_cols,
            "page": "smooth",
            **get_sidebar_context(active_file=None)
        }
    )


# ── 2️⃣ preview original series ─────────────────────────────
@router.post("/smooth/preview")
def preview(column: str = Form(...)):
    fp = get_active_csv_path()
    df = pd.read_csv(fp, usecols=[column])
    return {
        "x": list(range(len(df))),
        "y_raw": df[column].replace({np.nan: None}).tolist()
    }


# ── 3️⃣ apply smoothing and save csv ────────────────────────
@router.post("/smooth/apply")
def apply(
    column: str = Form(...),
    method: str = Form(...),
    frac: float = Form(0.1),
    kernel: int = Form(5),
    window: int = Form(7),
    n_sigmas: float = Form(3.0)
):
    fp = get_active_csv_path()
    df = pd.read_csv(fp)

    if column not in df.columns:
        raise HTTPException(400, "Selected column not found in dataset.")

    # Apply selected smoothing method
    if method == "lowess":
        smoothed = lowess_smooth(df[column], frac)
    elif method == "median":
        smoothed = median_filter(df[column], kernel)
    elif method == "hampel":
        smoothed = hampel_filter(df[column], window, n_sigmas)
    else:
        raise HTTPException(400, "Invalid smoothing method.")

    new_col = f"{column}_smoothed"
    df[new_col] = smoothed

    out_name = f"{fp.stem}_{column}_{method}.csv"
    out_fp = PROCESSED_DIR / out_name
    df.to_csv(out_fp, index=False)

    return {
        "x": list(range(len(df))),
        "y_raw": df[column].replace({np.nan: None}).tolist(),
        "y_smooth": smoothed.replace({np.nan: None}).tolist(),
        "out_file": out_name
    }


# ── 4️⃣ download smoothed result ────────────────────────────
@router.get("/smooth/download/{fname}")
def download(fname: str):
    fp = PROCESSED_DIR / fname
    if not fp.exists():
        raise HTTPException(404, "File not found.")
    return FileResponse(fp, media_type="text/csv", filename=fname)