import os
import pickle
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from backend.utils.regression.session_state import get_active_dataset

# ── Directory setup ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/models"))
PRED_DIR  = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/predictions"))

os.makedirs(SPLIT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PRED_DIR, exist_ok=True)


# ── List all saved models ─────────────────────────────────────────
def list_models() -> dict[str, str]:
    """
    Return a dictionary of model keys and filenames.
    """
    return {
        os.path.splitext(f)[0]: f
        for f in os.listdir(MODEL_DIR)
        if f.endswith(".pkl")
    }


# ── Load a model from disk ────────────────────────────────────────
def _load_model(key: str):
    """
    Load the model object (or bundle) given its key (filename without .pkl).
    """
    path = os.path.join(MODEL_DIR, f"{key}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model '{key}.pkl' not found.")
    with open(path, "rb") as f:
        return pickle.load(f)


# ── Load X_test or y_test ─────────────────────────────────────────
def _load_split(name: str) -> pd.DataFrame:
    """
    Load split CSV using active dataset's name as prefix.
    """
    base = Path(get_active_dataset()).stem
    fname = f"{base}_{name}.csv"
    path = os.path.join(SPLIT_DIR, fname)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{fname} not found — run prior steps.")
    return pd.read_csv(path)


# ── Predict using a model ─────────────────────────────────────────
def predict(model_key: str, df: pd.DataFrame, include_metrics: bool = False) -> tuple[pd.DataFrame, dict, str]:
    """
    Predict on given DataFrame using the specified model.

    Parameters
    ----------
    model_key : str
        Model identifier (from list_models()).
    df : pd.DataFrame
        Feature matrix to predict on (usually X_test_scaled).
    include_metrics : bool
        Whether to compute and return test set metrics.

    Returns
    -------
    preds_df : pd.DataFrame
        DataFrame with predictions.
    metrics : dict
        Evaluation metrics if `include_metrics` is True.
    output_file : str
        Path to saved prediction file.
    """
    obj = _load_model(model_key)

    # Handle model bundle (SVR case with y_scaler)
    if isinstance(obj, dict) and "model" in obj:
        model = obj["model"]
        y_scaler = obj.get("y_scaler")
        y_pred_scaled = model.predict(df).reshape(-1, 1)
        preds = (
            y_scaler.inverse_transform(y_pred_scaled).ravel()
            if y_scaler else
            y_pred_scaled.ravel()
        )
    else:
        model = obj
        preds = model.predict(df)

    # Attach source name to track origin (default to X_test)
    if "source_name" not in df.attrs or df.attrs["source_name"] == "X_test_scaled":
        df.attrs["source_name"] = get_active_dataset()

    # Save predictions
    base_name = Path(df.attrs["source_name"]).stem
    fname = f"{base_name}_{model_key}_predictions.csv"
    output_file = os.path.join(PRED_DIR, fname)

    preds_df = pd.DataFrame({"prediction": preds})
    preds_df.to_csv(output_file, index=False)

    # Optionally calculate evaluation metrics
    metrics = {}
    if include_metrics:
        y_true = _load_split("y_test").squeeze()
        metrics = {
            "mse": round(mean_squared_error(y_true, preds), 3),
            "rmse": round(np.sqrt(mean_squared_error(y_true, preds)), 3),
            "mae": round(mean_absolute_error(y_true, preds), 3),
            "r2":  round(r2_score(y_true, preds), 3),
        }

    return preds_df, metrics, output_file
