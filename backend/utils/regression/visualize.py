# utils/visualize.py

import os
import pandas as pd
import plotly.express as px
from plotly.io import to_html

# Path to cleaned data
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/static/uploads")
DATA_PATH = os.path.join(UPLOAD_DIR, "cleaned_data.csv")

def get_numeric_columns() -> list:
    """Return list of numeric column names from cleaned_data.csv."""
    try:
        df = pd.read_csv(DATA_PATH)
        return df.select_dtypes(include="number").columns.tolist()
    except Exception:
        return []

def load_cleaned_data() -> pd.DataFrame:
    """Load the cleaned dataset."""
    return pd.read_csv(DATA_PATH)

# Single-column visualizations (index vs column)
def make_scatter(df, column: str, limit: int) -> str:
    fig = px.scatter(df.head(limit), y=column, title=f"Scatter: Index vs {column}", template="plotly_white")
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)

def make_histogram(df, column: str, bins: int = 20) -> str:
    fig = px.histogram(df, x=column, nbins=bins, title=f"Histogram of {column}", template="plotly_white")
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)

# def make_boxplot(df, column: str) -> str:
#     fig = px.box(df, y=column, title=f"Box Plot of {column}", template="plotly_white")
#     fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
#     return to_html(fig, full_html=False)

# Two-column plots
def make_two_column_scatter(df, x_col: str, y_col: str) -> str:
    fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}", template="plotly_white")
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)

def make_two_column_histograms(df, cols: list) -> list:
    plots = []
    for col in cols:
        fig = px.histogram(df, x=col, nbins=20, title=f"Histogram of {col}", template="plotly_white")
        fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
        plots.append(to_html(fig, full_html=False))
    return plots

# def make_two_column_boxplots(df, cols: list) -> list:
#     plots = []
#     for col in cols:
#         fig = px.box(df, y=col, title=f"Box Plot of {col}", template="plotly_white")
#         fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
#         plots.append(to_html(fig, full_html=False))
#     return plots

def generate_visualizations(selected_columns: list, plot_types: list, scatter_limit: int = 100) -> list:
    """Generate Plotly HTML charts based on column count and plot types."""
    try:
        df = load_cleaned_data()
        plots = []

        if len(selected_columns) == 1:
            col = selected_columns[0]
            if "scatter" in plot_types:
                plots.append(make_scatter(df, col, scatter_limit))
            if "histogram" in plot_types:
                plots.append(make_histogram(df, col))
            # if "box" in plot_types:
            #     plots.append(make_boxplot(df, col))

        elif len(selected_columns) == 2:
            col1, col2 = selected_columns
            if "scatter" in plot_types:
                plots.append(make_two_column_scatter(df, col1, col2))
            if "histogram" in plot_types:
                plots.extend(make_two_column_histograms(df, [col1, col2]))
            # if "box" in plot_types:
            #     plots.extend(make_two_column_boxplots(df, [col1, col2]))

        return plots

    except Exception as e:
        return [f"<p class='text-danger'>Error generating plots: {e}</p>"]
