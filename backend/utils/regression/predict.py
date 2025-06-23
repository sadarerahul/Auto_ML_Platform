import os
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 📁 Directory paths (os-based)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/uploads"))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/models"))
PRED_DIR  = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/predictions"))

# Ensure directories exist
os.makedirs(SPLIT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PRED_DIR, exist_ok=True)

# 🔍 List all available models
def list_models() -> dict[str, str]:
    return {
        os.path.splitext(f)[0]: f
        for f in os.listdir(MODEL_DIR)
        if f.endswith(".pkl")
    }

# 📦 Load a model or model bundle
def _load_model(key: str):
    fp = os.path.join(MODEL_DIR, f"{key}.pkl")
    if not os.path.exists(fp):
        raise FileNotFoundError(f"Model '{key}.pkl' not found.")
    with open(fp, "rb") as f:
        return pickle.load(f)

# 📄 Load a dataset split (e.g. y_test)
def _load_split(name: str) -> pd.DataFrame:
    fp = os.path.join(SPLIT_DIR, f"{name}.csv")
    if not os.path.exists(fp):
        raise FileNotFoundError(f"{name}.csv not found — run prior steps.")
    return pd.read_csv(fp)

# 🔮 Predict and optionally evaluate
def predict(model_key: str, df: pd.DataFrame, include_metrics: bool = False):
    obj = _load_model(model_key)

    # Handle SVR bundle with target scaler
    if isinstance(obj, dict) and "model" in obj:
        model = obj["model"]
        y_scaler = obj.get("y_scaler")
        y_pred_scaled = model.predict(df).reshape(-1, 1)
        preds = (
            y_scaler.inverse_transform(y_pred_scaled).ravel()
            if y_scaler else y_pred_scaled.ravel()
        )
    else:
        model = obj
        preds = model.predict(df)

    preds_df = pd.DataFrame({"prediction": preds})

    # 💾 Save predictions
    output_file = os.path.join(PRED_DIR, f"{model_key}_predictions.csv")
    preds_df.to_csv(output_file, index=False)

    metrics = {}
    if include_metrics:
        y_true = _load_split("y_test").squeeze()
        metrics = {
            "mse": round(mean_squared_error(y_true, preds), 3),
            "rmse": round(np.sqrt(mean_squared_error(y_true, preds)), 3),
            "mae": round(mean_absolute_error(y_true, preds), 3),
            "r2": round(r2_score(y_true, preds), 3),
        }

    return preds_df, metrics, output_file