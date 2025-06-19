import pandas as pd
import plotly.express as px
from plotly.io import to_html
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
    fig.update_layout(height=400, margin=dict(l=80, r=20, t=60, b=40))
    return to_html(fig, full_html=False)

def top_features(series: pd.Series, k: int) -> list[str]:
    return series.head(k).index.tolist()
