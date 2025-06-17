import pandas as pd
from .paths import DATA_PATH

# internal cache (None until first request)
_CURRENT_DF = None

def _load_df():
    """Return the latest DataFrame in memory; read from disk if needed."""
    global _CURRENT_DF
    if _CURRENT_DF is None:
        _CURRENT_DF = pd.read_csv(DATA_PATH)
    return _CURRENT_DF

def _set_current_df(df):
    """Called by upload.py right after a new file is saved."""
    global _CURRENT_DF
    _CURRENT_DF = df.copy()

# ---------- public helpers ----------
def get_missing_columns():
    try:
        df = _load_df()
        return df.columns[df.isna().any()].tolist()
    except Exception:
        return []

def get_categorical_columns():
    try:
        df = _load_df()
        return df.select_dtypes(include=["object", "category"]).columns.tolist()
    except Exception:
        return []

def apply_missing_value_strategy(column, strategy, custom):
    df = _load_df()
    if column not in df.columns:
        return False, "❌ Column not found"

    if strategy == "drop":
        df.dropna(subset=[column], inplace=True)
    elif strategy == "mean":
        df[column].fillna(df[column].mean(), inplace=True)
    elif strategy == "median":
        df[column].fillna(df[column].median(), inplace=True)
    elif strategy == "mode":
        df[column].fillna(df[column].mode()[0], inplace=True)
    elif strategy == "custom":
        df[column].fillna(custom, inplace=True)
    else:
        return False, "❌ Unknown strategy"

    df.to_csv(DATA_PATH, index=False)
    _set_current_df(df)
    return True, "✅ Missing‑value handling applied"

def apply_encoding(column, strategy):
    df = _load_df()
    if column not in df.columns:
        return False, "❌ Column not found"

    if strategy == "onehot":
        df = pd.get_dummies(df, columns=[column])
    elif strategy == "label":
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column].astype(str))
    elif strategy == "freq":
        freq = df[column].value_counts() / len(df)
        df[column] = df[column].map(freq)
    else:
        return False, "❌ Unknown encoding"

    df.to_csv(DATA_PATH, index=False)
    _set_current_df(df)
    return True, "✅ Encoding applied"

def get_cleaned_data_preview(n=10):
    try:
        return _load_df().head(n).to_html(
            classes="table table-striped table-bordered",
            index=False
        )
    except Exception as exc:
        return f"<p class='text-danger'>❌ Preview failed: {exc}</p>"
