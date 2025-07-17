import pandas as pd
import plotly.express as px
from plotly.io import to_html
from .cleaning import load_data as _load_data


# Load Data
def load_cleaned_data() -> pd.DataFrame:
    """Return the cleaned dataset currently being processed."""
    return _load_data()


def get_numeric_columns() -> list:
    """Return numeric columns from the cleaned dataset."""
    try:
        df = _load_data()
        return df.select_dtypes(include="number").columns.tolist()
    except Exception:
        return []


# ---------- Visualization Helpers ----------
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


def make_scatter(df, x_col: str, y_col: str, limit: int = 100, dark=False) -> str:
    if x_col not in df.columns or y_col not in df.columns:
        return f"<p class='text-danger'>One or both columns not found: {x_col}, {y_col}</p>"
    data = df if limit is None else df.head(limit)
    fig = px.scatter(
        data,
        x=x_col,
        y=y_col,
        title=f"Scatter Plot: {y_col} vs {x_col}",
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)


def make_single_column_line(df, column: str, limit: int = 100, dark=False) -> str:
    """Creates a line plot of a single column against its index."""
    if column not in df.columns:
        return f"<p class='text-danger'>Column '{column}' not found.</p>"
    data = df if limit is None else df.head(limit)
    fig = px.line(
        data,
        x=data.index,
        y=column,
        title=f"Line Plot of {column} (Index vs {column})",
        template="plotly_dark" if dark else "plotly_white"
    )
    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))
    return to_html(fig, full_html=False)


# ---------- Main Visualization Generator ----------
def generate_visualizations(x_col: str, y_col: str, plot_types: list, scatter_limit: int = 100, dark=True) -> list:
    """
    Generate visualizations based on X column, optional Y column, and selected plot types.
    Supported plot_types: 'scatter', 'histogram', 'lineplot'
    """
    try:
        df = load_cleaned_data()
        if df.empty:
            return ["<p class='text-warning'>⚠️ Dataset is empty or could not be loaded.</p>"]

        plots = []

        # Validate X column
        if not x_col or x_col not in df.columns:
            return ["<p class='text-danger'>❌ Please select a valid X column.</p>"]

        # Histogram for X column
        if "histogram" in plot_types:
            plots.append(make_histogram(df, x_col, dark=dark))

        # Scatter Plot if Y provided
        if y_col and y_col in df.columns and "scatter" in plot_types:
            plots.append(make_scatter(df, x_col, y_col, scatter_limit, dark))

        # Line Plots: ONLY separate line plots for each selected column
        if "lineplot" in plot_types:
            plots.append(make_single_column_line(df, x_col, scatter_limit, dark))
            if y_col and y_col in df.columns:
                plots.append(make_single_column_line(df, y_col, scatter_limit, dark))

        return plots if plots else ["<p class='text-info'>ℹ️ No plots generated. Please select plot type(s).</p>"]

    except Exception as e:
        return [f"<p class='text-danger'>Error generating plots: {e}</p>"]
