import os
import numpy as np
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.signal import medfilt

from backend.utils.regression.session_state import get_active_dataset

UPLOAD_DIR = "frontend/static/uploads"
CLEANED_DIR = "frontend/static/cleaned"
os.makedirs(CLEANED_DIR, exist_ok=True)

def _get_cleaned_path() -> str | None:
    """Returns cleaned dataset path. Creates it from raw if missing."""
    filename = get_active_dataset()
    if not filename:
        return None

    raw_path = os.path.join(UPLOAD_DIR, filename)
    cleaned_name = filename.replace(".csv", "_cleaned.csv")
    cleaned_path = os.path.join(CLEANED_DIR, cleaned_name)

    if not os.path.exists(cleaned_path) and os.path.exists(raw_path):
        df = pd.read_csv(raw_path)
        df.to_csv(cleaned_path, index=False)

    return cleaned_path if os.path.exists(cleaned_path) else None

def _load_latest_dataset() -> tuple[pd.DataFrame, str] | tuple[None, None]:
    """Load the cleaned dataset if available."""
    cleaned_path = _get_cleaned_path()
    if not cleaned_path:
        return None, None
    df = pd.read_csv(cleaned_path)
    return df, cleaned_path

def lowess_smooth(series: pd.Series, frac: float = 0.1) -> pd.Series:
    x = np.arange(len(series))
    y = series.values
    smoothed = lowess(y, x, frac=frac, return_sorted=False)
    return pd.Series(smoothed, index=series.index)

def median_filter(series: pd.Series, kernel: int = 5) -> pd.Series:
    if kernel % 2 == 0:
        kernel += 1
    smoothed = medfilt(series, kernel_size=kernel)
    return pd.Series(smoothed, index=series.index)

def hampel_filter(series: pd.Series, window: int = 5, n_sigmas: int = 3) -> pd.Series:
    new_series = series.copy()
    k = 1.4826

    for i in range(window, len(series) - window):
        window_data = series[(i - window):(i + window + 1)]
        median = window_data.median()
        mad = k * (np.abs(window_data - median)).median()
        threshold = n_sigmas * mad
        if np.abs(series[i] - median) > threshold:
            new_series[i] = median

    return new_series

def apply_smoothing(column: str, method: str, window: int = 5, alpha: float = 0.1) -> str:
    """Apply smoothing method on active cleaned dataset."""
    df, path = _load_latest_dataset()
    if df is None or column not in df.columns:
        return f"❌ Dataset or column '{column}' not found."

    try:
        if method == "lowess":
            smoothed = lowess_smooth(df[column], frac=alpha)
        elif method == "median":
            smoothed = median_filter(df[column], kernel=window)
        elif method == "hampel":
            smoothed = hampel_filter(df[column], window=window)
        else:
            return f"❌ Unknown method '{method}'."

        df[column + "_smoothed"] = smoothed
        df.to_csv(path, index=False)
        return f"✅ {method.title()} smoothing applied to '{column}' and saved to cleaned dataset."
    except Exception as e:
        return f"❌ Error during smoothing: {str(e)}"
