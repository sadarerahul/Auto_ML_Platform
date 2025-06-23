import os
import pandas as pd
import plotly.express as px
from plotly.io import to_html
from .cleaning import load_data as _load_data

def get_numeric_columns() -> list:
    """Return numeric columns from the freshest dataset."""
    try:
        df = _load_data()
        return df.select_dtypes(include="number").columns.tolist()
    except Exception:
        return []

def load_cleaned_data() -> pd.DataFrame:
    """Return the freshest dataset (cleaned if available)."""
    return _load_data()

# Visualization helpers
def make_scatter(df, column: str, limit: int = 100, dark=False) -> str:
    fig = px.scatter(
        df.head(limit),
        y=column,
        title=f"Scatter: Index vs {column}",
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)

def make_histogram(df, column: str, bins: int = 20, dark=False) -> str:
    fig = px.histogram(
        df,
        x=column,
        nbins=bins,
        title=f"Histogram of {column}",
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)

def make_two_column_scatter(df, x_col: str, y_col: str, dark=False) -> str:
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        title=f"{x_col} vs {y_col}",
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)

def make_two_column_histograms(df, cols: list, dark=False) -> list:
    plots = []
    for col in cols:
        fig = px.histogram(
            df,
            x=col,
            nbins=20,
            title=f"Histogram of {col}",
            template="plotly_dark" if dark else "plotly_white"
        )
        fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
        plots.append(to_html(fig, full_html=False))
    return plots

def generate_visualizations(selected_columns: list, plot_types: list, scatter_limit: int = 100, dark=True) -> list:
    """Generate Plotly HTML charts based on column count and requested types (no boxplots)."""
    try:
        df = load_cleaned_data()
        plots = []

        if len(selected_columns) == 1:
            col = selected_columns[0]
            if "scatter" in plot_types:
                plots.append(make_scatter(df, col, scatter_limit, dark))
            if "histogram" in plot_types:
                plots.append(make_histogram(df, col, dark=dark))

        elif len(selected_columns) == 2:
            col1, col2 = selected_columns
            if "scatter" in plot_types:
                plots.append(make_two_column_scatter(df, col1, col2, dark))
            if "histogram" in plot_types:
                plots.extend(make_two_column_histograms(df, [col1, col2], dark))

        return plots

    except Exception as e:
        return [f"<p class='text-danger'>Error generating plots: {e}</p>"]