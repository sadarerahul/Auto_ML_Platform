import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from pathlib import Path
import re
from backend.utils.regression.session_state import set_active_dataset, get_active_dataset

pio.templates.default = "plotly_white"

# ────────────────────────────────────────────────────────────────
# 📁  Directory setup
# ────────────────────────────────────────────────────────────────
PLOT_PATH   = "frontend/static/plots"
UPLOAD_DIR  = "frontend/static/uploads"
CLEANED_DIR = "frontend/static/cleaned"
for d in (PLOT_PATH, UPLOAD_DIR, CLEANED_DIR):
    os.makedirs(d, exist_ok=True)

# ────────────────────────────────────────────────────────────────
# 🫼  Helpers
# ────────────────────────────────────────────────────────────────
def safe_filename(text: str) -> str:
    """Replace characters that are illegal on Windows or POSIX filesystems."""
    return re.sub(r'[<>:"/\\|?*]', "_", text)

# ────────────────────────────────────────────────────────────────
# 📊  Dataset-level helpers
# ────────────────────────────────────────────────────────────────
def dataset_overview(df: pd.DataFrame) -> dict:
    return {
        "shape": df.shape,
        "columns": df.dtypes.reset_index()
                     .rename(columns={"index": "Column", 0: "Dtype"})
                     .to_dict(orient="records"),
        "n_rows": df.shape[0],
        "n_cols": df.shape[1],
    }

def describe_data(df: pd.DataFrame):
    summary          = df.describe().T
    summary["median"] = df.median(numeric_only=True)
    try:
        summary["mode"] = df.mode(numeric_only=True).iloc[0]
    except IndexError:
        summary["mode"] = np.nan

    missing = pd.DataFrame({
        "missing_count"   : df.isna().sum(),
        "missing_percent" : df.isna().mean().mul(100)
    })
    return summary.round(2), missing.round(2)

# ────────────────────────────────────────────────────────────────
# 📉  Univariate plots
# ────────────────────────────────────────────────────────────────
def generate_univariate_plots(df: pd.DataFrame, dataset_name: str) -> list[str]:
    plots = []
    base  = Path(dataset_name).stem

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            fig = px.histogram(df, x=col, marginal="box", nbins=30,
                               title=f"Distribution of {col}")
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            vc  = df[col].value_counts().reset_index()
            vc.columns = [col, "count"]
            fig = px.bar(vc, x=col, y="count", title=f"Count plot of {col}")
        else:
            continue

        safe_col  = safe_filename(col)
        file_name = f"{base}_univariate_{safe_col}.html"
        file_path = os.path.join(PLOT_PATH, file_name)
        fig.write_html(file_path)
        plots.append(file_path.replace("frontend", ""))
    return plots

# ────────────────────────────────────────────────────────────────
# 🔗  Multivariate plots
# ────────────────────────────────────────────────────────────────
def generate_multivariate_plots(df: pd.DataFrame, dataset_name: str) -> list[str]:
    plots    = []
    base     = Path(dataset_name).stem
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        fig  = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
        path = os.path.join(PLOT_PATH, f"{base}_correlation.html")
        fig.write_html(path)
        plots.append(path.replace("frontend", ""))

    if 2 <= len(num_cols) <= 6:
        fig  = px.scatter_matrix(df, dimensions=num_cols, title="Pairplot Matrix")
        path = os.path.join(PLOT_PATH, f"{base}_pairplot.html")
        fig.write_html(path)
        plots.append(path.replace("frontend", ""))

    return plots

# ────────────────────────────────────────────────────────────────
# 🎯  Percentile filtering helper
# ────────────────────────────────────────────────────────────────
def filter_dataset_by_target(
    df: pd.DataFrame,
    target_col: str,
    lower_percentile: float,
    upper_percentile: float,
):
    if not (0 <= lower_percentile <= 100 and 0 <= upper_percentile <= 100):
        raise ValueError("Percentiles must be between 0 and 100.")
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found.")

    lower = df[target_col].quantile(lower_percentile / 100)
    upper = df[target_col].quantile(upper_percentile / 100)
    filtered_df = df[df[target_col].between(lower, upper)].copy()

    # ✅ Always save to "<base>_cleaned.csv"
    current_active = Path(get_active_dataset()).stem
    base_name = current_active.replace("_cleaned", "")
    file_name = f"{base_name}_cleaned.csv"
    cleaned_path = os.path.join(CLEANED_DIR, file_name)

    filtered_df.to_csv(cleaned_path, index=False)

    # ❌ Don't set this cleaned file as active
    # set_active_dataset(file_name) ← REMOVE THIS LINE

    shape_str = f"{filtered_df.shape[0]} rows × {filtered_df.shape[1]} columns"
    return filtered_df, shape_str, file_name

