import os
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from backend.utils.regression.session_state import get_active_dataset

# 📁 Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/models"))
PRED_DIR  = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/predictions"))

os.makedirs(SPLIT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PRED_DIR, exist_ok=True)

# 🔍 List all models
def list_models() -> dict[str, str]:
    return {
        os.path.splitext(f)[0]: f
        for f in os.listdir(MODEL_DIR)
        if f.endswith(".pkl")
    }

# 🎯 Load a model by key
def _load_model(key: str):
    path = os.path.join(MODEL_DIR, f"{key}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model '{key}.pkl' not found.")
    with open(path, "rb") as f:
        return pickle.load(f)

# 📄 Load a dataset split file, dataset-prefixed
def _load_split(name: str) -> pd.DataFrame:
    base = Path(get_active_dataset()).stem
    fname = f"{base}_{name}.csv"
    path = os.path.join(SPLIT_DIR, fname)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{fname} not found — run prior steps.")
    return pd.read_csv(path)

# 🔮 Make predictions
def predict(model_key: str, df: pd.DataFrame, include_metrics: bool = False):
    obj = _load_model(model_key)

    # Handle SVR bundle with optional scaler
    if isinstance(obj, dict) and "model" in obj:
        model = obj["model"]
        y_scaler = obj.get("y_scaler")
        y_pred_scaled = model.predict(df).reshape(-1, 1)
        preds = y_scaler.inverse_transform(y_pred_scaled).ravel() if y_scaler else y_pred_scaled.ravel()
    else:
        model = obj
        preds = model.predict(df)

    # 🏷 Ensure source_name is set
    if "source_name" not in df.attrs or df.attrs["source_name"] == "X_test_scaled":
        df.attrs["source_name"] = get_active_dataset()

    # 📊 Save predictions
    preds_df = pd.DataFrame({"prediction": preds})
    base_name = Path(df.attrs["source_name"]).stem
    fname = f"{base_name}_{model_key}_predictions.csv"
    output_file = os.path.join(PRED_DIR, fname)
    preds_df.to_csv(output_file, index=False)

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