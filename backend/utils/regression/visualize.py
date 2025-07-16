import os
import pandas as pd
import plotly.express as px
from plotly.io import to_html
from .cleaning import load_data as _load_data


def get_numeric_columns() -> list:
    """Return numeric columns from the cleaned dataset currently being processed."""
    try:
        df = _load_data()
        return df.select_dtypes(include="number").columns.tolist()
    except Exception:
        return []


def load_cleaned_data() -> pd.DataFrame:
    """Return the cleaned dataset currently being processed."""
    return _load_data()


# ---------- Visualization Helpers ----------

def make_scatter(df, column: str, limit: int = 100, dark=False) -> str:
    if column not in df.columns:
        return f"<p class='text-danger'>Column '{column}' not found in dataset.</p>"

    data = df if limit is None else df.head(limit)
    fig = px.scatter(
        data,
        y=column,
        title=f"Scatter: Index vs {column}",
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)


def make_histogram(df, column: str, bins: int = 20, dark=False) -> str:
    if column not in df.columns:
        return f"<p class='text-danger'>Column '{column}' not found in dataset.</p>"

    fig = px.histogram(
        df,
        x=column,
        nbins=bins,
        title=f"Histogram of {column}",
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)


def make_lineplot(df, column: str, limit: int = 100, dark=False) -> str:
    if column not in df.columns:
        return f"<p class='text-danger'>Column '{column}' not found in dataset.</p>"
    
    data = df if limit is None else df.head(limit)
    fig = px.line(
        data,
        x=data.index,
        y=column,
        title=f"Line Plot: Index vs {column}",
        labels={'x': 'Index', column: column},
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)


def make_two_column_scatter(df, x_col: str, y_col: str, limit: int = 100, dark=False) -> str:
    if x_col not in df.columns or y_col not in df.columns:
        return f"<p class='text-danger'>One or both columns not found: {x_col}, {y_col}</p>"

    data = df if limit is None else df.head(limit)
    fig = px.scatter(
        data,
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
        if col not in df.columns:
            plots.append(f"<p class='text-danger'>Column '{col}' not found.</p>")
            continue
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


def make_two_column_lineplot(df, cols: list, limit: int = 100, dark=False) -> list:
    plots = []
    data = df if limit is None else df.head(limit)
    for col in cols:
        if col not in df.columns:
            plots.append(f"<p class='text-danger'>Column '{col}' not found.</p>")
            continue
        fig = px.line(
            data,
            x=data.index,
            y=col,
            title=f"Line Plot: Index vs {col}",
            labels={'x': 'Index', col: col},
            template="plotly_dark" if dark else "plotly_white"
        )
        fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
        plots.append(to_html(fig, full_html=False))
    return plots


# ---------- Main Generator ----------

def generate_visualizations(selected_columns: list, plot_types: list, scatter_limit: int = 100, dark=True) -> list:
    """
    Generate Plotly HTML charts based on selected columns and plot types.
    Supported plot_types: 'scatter', 'histogram', 'lineplot'
    """
    try:
        df = load_cleaned_data()
        if df.empty:
            return ["<p class='text-warning'>⚠️ Dataset is empty or could not be loaded.</p>"]

        plots = []

        if len(selected_columns) == 1:
            col = selected_columns[0]
            if "scatter" in plot_types:
                plots.append(make_scatter(df, col, scatter_limit, dark))
            if "histogram" in plot_types:
                plots.append(make_histogram(df, col, dark=dark))
            if "lineplot" in plot_types:
                plots.append(make_lineplot(df, col, scatter_limit, dark))

        elif len(selected_columns) == 2:
            col1, col2 = selected_columns
            if "scatter" in plot_types:
                plots.append(make_two_column_scatter(df, col1, col2, scatter_limit, dark))
            if "histogram" in plot_types:
                plots.extend(make_two_column_histograms(df, [col1, col2], dark))
            if "lineplot" in plot_types:
                plots.extend(make_two_column_lineplot(df, [col1, col2], scatter_limit, dark))

        return plots

    except Exception as e:
        return [f"<p class='text-danger'>Error generating plots: {e}</p>"]
