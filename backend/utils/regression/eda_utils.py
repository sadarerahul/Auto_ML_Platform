# backend/utils/regression/eda_utils.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.io as pio
import os
from fastapi import APIRouter, Request, Form

pio.templates.default = "plotly_white"

PLOT_PATH = "frontend/static/plots"
os.makedirs(PLOT_PATH, exist_ok=True)

def dataset_overview(df: pd.DataFrame) -> dict:
    return {
        "shape": df.shape,
        "columns": df.dtypes.reset_index().rename(columns={"index": "Column", 0: "Dtype"}).to_dict(orient="records"),
        "n_rows": df.shape[0],
        "n_cols": df.shape[1],
    }

def describe_data(df: pd.DataFrame):
    summary = df.describe().T
    summary["median"] = df.median(numeric_only=True)
    summary["mode"] = df.mode(numeric_only=True).iloc[0]
    missing = pd.DataFrame({
        "missing_count": df.isnull().sum(),
        "missing_percent": df.isnull().mean() * 100
    })
    return summary.round(2), missing.round(2)

def generate_univariate_plots(df: pd.DataFrame):
    plots = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            fig = px.histogram(df, x=col, marginal="box", nbins=30, title=f"Distribution of {col}")
        elif pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == object:
            value_counts = df[col].value_counts().reset_index()
            value_counts.columns = [col, "count"]
            fig = px.bar(value_counts, x=col, y="count", title=f"Count plot of {col}", labels={col: col, "count": "Count"})
        else:
            continue

        plot_path = os.path.join(PLOT_PATH, f"univariate_{col}.html")
        fig.write_html(plot_path)
        plots.append(plot_path.replace("frontend", ""))
    return plots

def generate_multivariate_plots(df: pd.DataFrame):
    plots = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
        path = os.path.join(PLOT_PATH, "correlation.html")
        fig.write_html(path)
        plots.append(path.replace("frontend", ""))

    if len(num_cols) <= 6:
        sns.pairplot(df[num_cols])
        path = os.path.join(PLOT_PATH, "pairplot.png")
        plt.savefig(path)
        plt.clf()
        plots.append(path.replace("frontend", ""))

    return plots

# Add this at the bottom of backend/utils/regression/eda_utils.py

import os
import pandas as pd

def filter_dataset_by_target(df, target_col, lower_percentile, upper_percentile):
    # Convert to float and divide by 100 to get into range [0, 1]
    lower_p = float(lower_percentile) / 100.0
    upper_p = float(upper_percentile) / 100.0

    if not (0 <= lower_p <= 1 and 0 <= upper_p <= 1):
        raise ValueError("Percentiles must be between 0 and 100.")

    q1 = df[target_col].quantile(lower_p)
    q3 = df[target_col].quantile(upper_p)

    filtered_df = df[(df[target_col] >= q1) & (df[target_col] <= q3)]
    shape_str = f"{filtered_df.shape[0]} rows × {filtered_df.shape[1]} columns"

    filename = f"filtered_{target_col}_{int(lower_percentile)}_{int(upper_percentile)}.csv"
    filepath = os.path.join("frontend/static/uploads", filename)
    filtered_df.to_csv(filepath, index=False)

    return filtered_df, shape_str, filename
