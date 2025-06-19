import os, pickle
import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_squared_error, r2_score

SPLIT_DIR  = Path("frontend/static/splits")
MODEL_DIR  = Path("frontend/static/models")
PRED_DIR   = Path("frontend/static/predictions")
PRED_DIR.mkdir(parents=True, exist_ok=True)

def list_models() -> dict[str, str]:
    """Return dict key->filename for all .pkl models."""
    return {f.stem: f.name for f in MODEL_DIR.glob("*.pkl")}

def _load_model(key: str):
    fp = MODEL_DIR / f"{key}.pkl"
    with open(fp, "rb") as f:
        obj = pickle.load(f)
    return obj

def _load_split(name: str) -> pd.DataFrame:
    fp = SPLIT_DIR / f"{name}.csv"
    if not fp.exists():
        raise FileNotFoundError(f"{fp.name} not found – run prior steps.")
    return pd.read_csv(fp)

def predict(model_key: str, df: pd.DataFrame, include_metrics: bool = False):
    obj = _load_model(model_key)

    # handle SVR bundle
    if isinstance(obj, dict) and "model" in obj:
        model  = obj["model"]
        y_scaler = obj["y_scaler"]
        y_pred_scaled = model.predict(df).reshape(-1,1)
        preds = y_scaler.inverse_transform(y_pred_scaled).ravel()
    else:
        model = obj
        preds = model.predict(df)

    preds_df = pd.DataFrame({"prediction": preds})

    metrics = {}
    if include_metrics:
        y_true = _load_split("y_test").squeeze()
        metrics["mse"] = mean_squared_error(y_true, preds)
        metrics["r2"]  = r2_score(y_true, preds)

    return preds_df, metrics
