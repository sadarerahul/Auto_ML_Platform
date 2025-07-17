import os
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import re

# Set default Plotly theme
px.defaults.template = "plotly_white"

# ─────────────────────────────
# 📂 Directory Setup
# ─────────────────────────────
PLOTS_DIR = "frontend/static/plots"
UPLOAD_DIR = "frontend/static/uploads"
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─────────────────────────────
# ✅ Helpers
# ─────────────────────────────
def safe_filename(text: str) -> str:
    """Generate a filesystem-safe filename by replacing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', "_", text)


# ─────────────────────────────
# 📊 Dataset Overview
# ─────────────────────────────
def dataset_overview(df: pd.DataFrame) -> dict:
    """Return basic dataset details: shape, columns, dtypes."""
    return {
        "shape": df.shape,
        "n_rows": df.shape[0],
        "n_cols": df.shape[1],
        "columns": df.dtypes.reset_index()
                     .rename(columns={"index": "Column", 0: "Dtype"})
                     .to_dict(orient="records")
    }


def describe_data(df: pd.DataFrame):
    """Return summary stats and missing value info."""
    summary = df.describe().T
    summary["median"] = df.median(numeric_only=True)
    try:
        summary["mode"] = df.mode(numeric_only=True).iloc[0]
    except IndexError:
        summary["mode"] = np.nan

    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percent": df.isna().mean() * 100
    })

    return summary.round(2), missing.round(2)


# ─────────────────────────────
# 📈 Univariate Plots
# ─────────────────────────────
def generate_univariate_plots(df: pd.DataFrame, dataset_name: str) -> list:
    """Generate distribution or count plots for each column."""
    plots = []
    base_name = Path(dataset_name).stem

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            fig = px.histogram(df, x=col, nbins=30, marginal="box",
                               title=f"Distribution of {col}")
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            vc = df[col].value_counts().reset_index()
            vc.columns = [col, "count"]
            fig = px.bar(vc, x=col, y="count", title=f"Count plot of {col}")
        else:
            continue

        safe_col = safe_filename(col)
        plot_file = os.path.join(PLOTS_DIR, f"{base_name}_uni_{safe_col}.html")
        fig.write_html(plot_file)
        plots.append(plot_file.replace("frontend", ""))  # relative path
    return plots


# ─────────────────────────────
# 🔗 Multivariate Plots
# ─────────────────────────────
def generate_multivariate_plots(df: pd.DataFrame, dataset_name: str) -> list:
    """Generate correlation heatmap and pairplot for numeric columns."""
    plots = []
    base_name = Path(dataset_name).stem
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Correlation Heatmap
    if len(num_cols) >= 2:
        fig = px.imshow(df[num_cols].corr(), text_auto=True, title="Correlation Heatmap")
        heatmap_file = os.path.join(PLOTS_DIR, f"{base_name}_correlation.html")
        fig.write_html(heatmap_file)
        plots.append(heatmap_file.replace("frontend", ""))

    # Pairplot (only if 2-6 numeric columns)
    if 2 <= len(num_cols) <= 6:
        fig = px.scatter_matrix(df, dimensions=num_cols, title="Pairplot Matrix")
        pairplot_file = os.path.join(PLOTS_DIR, f"{base_name}_pairplot.html")
        fig.write_html(pairplot_file)
        plots.append(pairplot_file.replace("frontend", ""))

    return plots
