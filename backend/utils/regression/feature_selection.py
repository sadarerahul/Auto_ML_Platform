import pandas as pd
import plotly.express as px
from plotly.io import to_html
from .cleaning import load_data

# ---------- Core Utilities ----------

def numeric_columns() -> list[str]:
    """Returns numeric columns from the current dataset."""
    df = load_data()
    return df.select_dtypes(include="number").columns.tolist()

def correlation_with_target(target: str, fillna: bool = True) -> pd.Series:
    """
    Computes Pearson correlation between all numeric features and the target column.

    Parameters
    ----------
    target : str
        The target variable name.
    fillna : bool
        Whether to fill missing values with mean before computing correlation.

    Returns
    -------
    pd.Series
        Sorted correlations (absolute value) with the target column.
    """
    df = load_data()
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found.")
    df = df.select_dtypes(include="number")
    if fillna:
        df = df.fillna(df.mean())
    corr = df.corr(numeric_only=True)
    return corr[target].drop(labels=[target]).sort_values(key=abs, ascending=False)

def correlation_bar_html(series: pd.Series, title: str = "") -> str:
    """
    Creates an interactive horizontal bar chart for correlations.

    Parameters
    ----------
    series : pd.Series
        Correlation scores indexed by feature name.
    title : str
        Title of the chart.

    Returns
    -------
    str
        HTML of the Plotly chart.
    """
    fig = px.bar(
        series[::-1],  # reverse for descending order
        x=series.values,
        y=series.index,
        orientation="h",
        title=title,
        template="plotly_white"
    )
    fig.update_traces(text=series[::-1].round(3).values, textposition='auto')
    fig.update_layout(height=400, margin=dict(l=80, r=20, t=60, b=40))
    return to_html(fig, full_html=False)

def top_features(series: pd.Series, k: int) -> list[str]:
    """
    Returns top-k feature names from a ranked correlation/mutual info series.

    Parameters
    ----------
    series : pd.Series
        Ranked feature importance scores.
    k : int
        Number of top features to select.

    Returns
    -------
    list[str]
        List of top-k feature names.
    """
    return series.head(k).index.tolist()

# Optional: Mutual Information Variant
# from sklearn.feature_selection import mutual_info_regression
# def mutual_info_with_target(target: str) -> pd.Series:
#     df = load_data().select_dtypes(include="number").dropna()
#     if target not in df.columns:
#         raise ValueError(f"Target '{target}' not found.")
#     X = df.drop(columns=[target])
#     y = df[target]
#     mi = mutual_info_regression(X, y)
#     return pd.Series(mi, index=X.columns).sort_values(ascending=False)
