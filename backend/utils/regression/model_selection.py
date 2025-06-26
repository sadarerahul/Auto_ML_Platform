import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from backend.utils.regression.session_state import get_active_dataset

# 🔐 Storage directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/models"))

os.makedirs(SPLIT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# 📄 Load dataset-prefixed split
def _load(name: str) -> pd.DataFrame:
    base = Path(get_active_dataset()).stem
    filename = f"{base}_{name}.csv"
    path = os.path.join(SPLIT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} not found — run previous steps.")
    return pd.read_csv(path)

# 🧠 Supported models
def available_models() -> dict[str, tuple[str, object]]:
    return {
        "linear": ("Linear Regression", LinearRegression()),
        "dtr":    ("Decision Tree",     DecisionTreeRegressor(random_state=42)),
        "rf":     ("Random Forest",     RandomForestRegressor(n_estimators=100, random_state=42)),
        "svr":    ("Support Vector Regression", SVR(kernel="rbf")),
    }

# 🧪 Train & save models with versioned names
def train_and_evaluate(model_keys: list[str], dataset_name: str) -> pd.DataFrame:
    X_train = _load("X_train_scaled")
    X_test  = _load("X_test_scaled")
    y_train = _load("y_train").squeeze()
    y_test  = _load("y_test").squeeze()

    results = []
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    base_name = os.path.splitext(dataset_name)[0]

    for key in model_keys:
        label, model = available_models()[key]

        if key == "svr":
            y_scaler = StandardScaler()
            y_train_scaled = y_scaler.fit_transform(y_train.to_numpy().reshape(-1, 1)).ravel()
            model.fit(X_train, y_train_scaled)
            y_pred_scaled = model.predict(X_test).reshape(-1, 1)
            y_pred = y_scaler.inverse_transform(y_pred_scaled).ravel()
            model_bundle = {"model": model, "y_scaler": y_scaler}
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            model_bundle = {"model": model, "y_scaler": None}

        # 📦 Save model with dataset + model + timestamp
        fname = f"{base_name}_{key}_{timestamp}.pkl"
        model_path = os.path.join(MODEL_DIR, fname)
        with open(model_path, "wb") as f:
            pickle.dump(model_bundle, f)

        # 📊 Evaluate
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2  = r2_score(y_test, y_pred)

        results.append({
            "Model": label,
            "Filename": fname,
            "MSE": round(mse, 3),
            "RMSE": round(rmse, 3),
            "MAE": round(mae, 3),
            "R²": round(r2, 3),
        })

    return pd.DataFrame(results)