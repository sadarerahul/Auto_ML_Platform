import pandas as pd
import plotly.graph_objects as go
import os
from .cleaning import load_data as _load_data
from backend.utils.regression.session_state import get_processing_dataset_path

PLOT_PATH = "frontend/static/plots"
os.makedirs(PLOT_PATH, exist_ok=True)

def generate_comparison_histograms(df, target_col, feature_cols, lower_percentile=25, upper_percentile=75):
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found.")

    for col in feature_cols:
        if col not in df.columns:
            raise ValueError(f"Feature column '{col}' not found.")

    q1 = df[target_col].quantile(lower_percentile / 100)
    q3 = df[target_col].quantile(upper_percentile / 100)

    lower_group = df[df[target_col] <= q1]
    upper_group = df[df[target_col] >= q3]

    plot_paths = []

    for feature in feature_cols:
        fig = go.Figure()

        # Add histogram traces
        fig.add_trace(go.Histogram(
            x=lower_group[feature],
            name=f"Lower {lower_percentile}%",
            marker_color="blue",
            opacity=0.6
        ))

        fig.add_trace(go.Histogram(
            x=upper_group[feature],
            name=f"Upper {upper_percentile}%",
            marker_color="red",
            opacity=0.6
        ))

        # Add mean lines
        lower_avg = lower_group[feature].mean()
        upper_avg = upper_group[feature].mean()

        fig.add_vline(
            x=lower_avg,
            line=dict(color="blue", dash="dash"),
            annotation_text=f"Lower Avg: {lower_avg:.2f}",
            annotation_position="top left",
            annotation_font_color="blue"
        )

        fig.add_vline(
            x=upper_avg,
            line=dict(color="red", dash="dash"),
            annotation_text=f"Upper Avg: {upper_avg:.2f}",
            annotation_position="top right",
            annotation_font_color="red"
        )

        fig.update_layout(
            barmode='overlay',
            title=f"{feature} Distribution by Target Quartiles",
            xaxis_title=feature,
            yaxis_title="Count",
            template="plotly_white"
        )

        filename = f"compare_{feature}.html"
        filepath = os.path.join(PLOT_PATH, filename)
        fig.write_html(filepath)
        plot_paths.append(filepath.replace("frontend", ""))

    return plot_paths

def load_data():
    path = get_processing_dataset_path()
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()