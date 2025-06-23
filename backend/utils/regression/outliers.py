import os
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import skew, kurtosis
from backend.utils.regression.session_state import get_active_dataset

# 📁 Dataset paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/uploads"))
CLEANED_DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/cleaned"))
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)

# ✅ Save dataframe safely
def _safe_write(df, path):
    df.to_csv(path, index=False)

# 🔍 Resolve cleaned path in backend-only storage
def _get_cleaned_path():
    filename = get_active_dataset()
    if not filename:
        return None

    cleaned_name = filename.replace(".csv", "_cleaned.csv")
    cleaned_path = os.path.join(CLEANED_DATA_DIR, cleaned_name)
    raw_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(cleaned_path) and os.path.exists(raw_path):
        df = pd.read_csv(raw_path)
        _safe_write(df.head(500), cleaned_path)

    return cleaned_path if os.path.exists(cleaned_path) else None

# 🔢 List numeric columns
def get_numeric_columns_for_outliers():
    path = _get_cleaned_path()
    if not path:
        return []
    try:
        df = pd.read_csv(path)
        return df.select_dtypes(include=["number"]).columns.tolist()
    except Exception:
        return []

# 📊 Generate boxplot and suggest method
def generate_outlier_plot(column: str):
    path = _get_cleaned_path()
    if not path:
        return None, None
    try:
        df = pd.read_csv(path)
        if column not in df.columns:
            return None, None

        col_data = df[column].dropna()
        skew_val = skew(col_data)
        kurt_val = kurtosis(col_data, fisher=False)

        if abs(skew_val) < 0.5 and kurt_val < 3.5:
            suggestion = "zscore"
        elif abs(skew_val) < 1.0:
            suggestion = "iqr"
        else:
            suggestion = "capping"

        fig = px.box(df, y=column, template="plotly_dark", points="all")
        fig.update_layout(
            title=f"Outlier Distribution: {column}",
            yaxis_title=column,
            margin=dict(l=30, r=30, t=40, b=20),
            height=400
        )

        return fig.to_html(full_html=False, config={"displayModeBar": False}), suggestion
    except Exception:
        return None, None

# 🧮 Apply outlier handling method
def handle_outliers(column: str, method: str):
    path = _get_cleaned_path()
    if not path:
        return None, None, "⚠️ No active dataset found."

    try:
        df = pd.read_csv(path)
        if column not in df.columns:
            return None, None, f"❌ Column '{column}' not found."

        summary_before = df[column].describe().to_frame(name="Before")
        rows_before = len(df)

        if method == "iqr":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            df = df[(df[column] >= lower) & (df[column] <= upper)]
        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()
            if std == 0:
                return None, None, f"⚠️ Column '{column}' has zero variance — cannot apply z-score."
            df = df[np.abs((df[column] - mean) / std) <= 3]
        elif method == "capping":
            lower_cap = df[column].quantile(0.05)
            upper_cap = df[column].quantile(0.95)
            df[column] = np.where(df[column] < lower_cap, lower_cap, df[column])
            df[column] = np.where(df[column] > upper_cap, upper_cap, df[column])
        else:
            return None, None, f"❌ Unknown outlier method: {method}"

        summary_after = df[column].describe().to_frame(name="After")
        _safe_write(df.head(500), path)

        rows_after = len(df)
        delta = rows_before - rows_after
        note = f"✅ {method.upper()} applied to '{column}'."
        if method in ["iqr", "zscore"]:
            note += f" {delta} rows removed."
        elif method == "capping":
            note += " Values were capped between 5th and 95th percentile."

        return (
            summary_before.to_html(classes="table table-bordered table-sm"),
            summary_after.to_html(classes="table table-bordered table-sm"),
            note
        )
    except Exception as e:
        return None, None, f"❌ Error during outlier handling: {str(e)}"