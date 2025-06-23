import pandas as pd
import plotly.express as px
from plotly.io import to_html
<<<<<<< HEAD
from .cleaning import load_data

# Optional: Uncomment for mutual info support
# from sklearn.feature_selection import mutual_info_regression

# ---------- Core Utilities ----------

def numeric_columns() -> list[str]:
    """Returns numeric columns from the current dataset."""
    df = load_data()
    return df.select_dtypes(include="number").columns.tolist()

def correlation_with_target(target: str, fillna: bool = True) -> pd.Series:
    """Computes Pearson correlation between all numeric features and the target column."""
    df = load_data()
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found.")
    df = df.select_dtypes(include="number")
    if fillna:
        df = df.fillna(df.mean())
    corr = df.corr(numeric_only=True)
    return corr[target].drop(labels=[target]).sort_values(key=abs, ascending=False)

def correlation_bar_html(series: pd.Series, title: str = "") -> str:
    """Creates a horizontal bar chart for correlations."""
    fig = px.bar(
        series[::-1],
        x=series.values,
        y=series.index,
        orientation="h",
        title=title,
        template="plotly_white"
    )
    fig.update_traces(text=series[::-1].round(3).values, textposition='auto')
=======
from .cleaning import load_data   # freshest dataset

# ---------- helpers ----------
def numeric_columns() -> list[str]:
    df = load_data()
    return df.select_dtypes(include="number").columns.tolist()

def correlation_with_target(target: str) -> pd.Series:
    df = load_data()
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found.")
    corr = df.corr(numeric_only=True)
    series = corr[target].drop(labels=[target]).sort_values(key=abs, ascending=False)
    return series

def correlation_bar_html(series: pd.Series, title: str) -> str:
    fig = px.bar(
        series[::-1], x=series.values, y=series.index,
        orientation="h", title=title, template="plotly_white"
    )
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
    fig.update_layout(height=400, margin=dict(l=80, r=20, t=60, b=40))
    return to_html(fig, full_html=False)

def top_features(series: pd.Series, k: int) -> list[str]:
<<<<<<< HEAD
    """Returns top-k feature names from a ranked series."""
    return series.head(k).index.tolist()

# Optional: Mutual Information Variant
# def mutual_info_with_target(target: str) -> pd.Series:
#     df = load_data().select_dtypes(include="number").dropna()
#     if target not in df.columns:
#         raise ValueError(f"Target '{target}' not found.")
#     X = df.drop(columns=[target])
#     y = df[target]
#     mi = mutual_info_regression(X, y)
#     return pd.Series(mi, index=X.columns).sort_values(ascending=False)
=======
    return series.head(k).index.tolist()
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
