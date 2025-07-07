import os
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from backend.utils.regression.session_state import get_active_dataset

# ── Directory Setup ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
os.makedirs(SPLIT_DIR, exist_ok=True)


# ── Load split file with dataset prefix ───────────────────────────
def _load_split(name: str) -> pd.DataFrame:
    """
    Load a split CSV file with dataset name prefix.

    Parameters
    ----------
    name : str
        One of "X_train", "X_test", etc.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.
    """
    base = Path(get_active_dataset()).stem
    filename = f"{base}_{name}.csv"
    path = os.path.join(SPLIT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} not found. Run Train‑Test Split first.")
    return pd.read_csv(path)


# ── Apply Scaler to Train/Test Splits ─────────────────────────────
def apply_scaler(scaler_type: str) -> dict:
    """
    Apply the selected scaler to X_train and X_test splits.

    Parameters
    ----------
    scaler_type : str
        "standard" for StandardScaler, "minmax" for MinMaxScaler.

    Returns
    -------
    dict
        Preview (head) of scaled X_train and X_test DataFrames.
    """
    base = Path(get_active_dataset()).stem
    X_train = _load_split("X_train")
    X_test = _load_split("X_test")

    if scaler_type == "standard":
        scaler = StandardScaler()
    elif scaler_type == "minmax":
        scaler = MinMaxScaler(feature_range=(0, 1))
    else:
        raise ValueError("Scaler type must be 'standard' or 'minmax'.")

    # Apply scaling
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

    # Save scaled splits
    X_train_scaled.to_csv(os.path.join(SPLIT_DIR, f"{base}_X_train_scaled.csv"), index=False)
    X_test_scaled.to_csv(os.path.join(SPLIT_DIR, f"{base}_X_test_scaled.csv"), index=False)

    return {
        "X_train_scaled": X_train_scaled.head(5),
        "X_test_scaled": X_test_scaled.head(5),
    }
