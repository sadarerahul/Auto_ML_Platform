<<<<<<< HEAD
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 🔐 Backend-only storage paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/uploads"))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/models"))

os.makedirs(SPLIT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# ------------ Helpers ------------

def _load(name: str) -> pd.DataFrame:
    fp = os.path.join(SPLIT_DIR, f"{name}.csv")
    if not os.path.exists(fp):
        raise FileNotFoundError(f"{name}.csv not found — run previous steps.")
    return pd.read_csv(fp)

def available_models() -> dict[str, tuple[str, object]]:
    """Maps model keys to (display label, model instance)."""
=======
import pandas as pd, pickle
from pathlib import Path
from sklearn.linear_model    import LinearRegression
from sklearn.tree            import DecisionTreeRegressor
from sklearn.ensemble        import RandomForestRegressor
from sklearn.svm             import SVR
from sklearn.preprocessing   import StandardScaler
from sklearn.metrics         import mean_squared_error, r2_score
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import pickle

from sklearn.preprocessing import StandardScaler

SPLIT_DIR = Path("frontend/static/splits")
MODEL_DIR = Path("frontend/static/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ------------ helpers ------------
def _load(name: str) -> pd.DataFrame:
    fp = SPLIT_DIR / f"{name}.csv"
    if not fp.exists():
        raise FileNotFoundError(f"{fp.name} not found – run previous steps.")
    return pd.read_csv(fp)

def available_models() -> dict[str, tuple[str, object]]:
    """
    key -> (label, instance)
    """
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
    return {
        "linear": ("Linear Regression", LinearRegression()),
        "dtr":    ("Decision Tree",     DecisionTreeRegressor(random_state=42)),
        "rf":     ("Random Forest",     RandomForestRegressor(n_estimators=100, random_state=42)),
        "svr":    ("Support Vector Regression", SVR(kernel="rbf")),
    }

<<<<<<< HEAD
# ------------ Main Routine ------------

=======
# ------------ main routine ------------
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
def train_and_evaluate(model_keys: list[str]) -> pd.DataFrame:
    X_train = _load("X_train_scaled")
    X_test  = _load("X_test_scaled")
    y_train = _load("y_train").squeeze()
    y_test  = _load("y_test").squeeze()

    results = []

    for key in model_keys:
        label, model = available_models()[key]

        if key == "svr":
            y_scaler = StandardScaler()
<<<<<<< HEAD
            y_train_scaled = y_scaler.fit_transform(y_train.to_numpy().reshape(-1, 1)).ravel()
            model.fit(X_train, y_train_scaled)
            y_pred_scaled = model.predict(X_test).reshape(-1, 1)
            y_pred = y_scaler.inverse_transform(y_pred_scaled).ravel()

            with open(os.path.join(MODEL_DIR, f"{key}.pkl"), "wb") as f:
                pickle.dump({"model": model, "y_scaler": y_scaler}, f)

=======
            y_train_scaled = y_scaler.fit_transform(y_train.to_numpy().reshape(-1,1)).ravel()

            model.fit(X_train, y_train_scaled)
            y_pred_scaled = model.predict(X_test).reshape(-1,1)
            y_pred = y_scaler.inverse_transform(y_pred_scaled).ravel()

            with open(MODEL_DIR / f"{key}.pkl", "wb") as f:
                pickle.dump({"model": model, "y_scaler": y_scaler}, f)
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

<<<<<<< HEAD
            with open(os.path.join(MODEL_DIR, f"{key}.pkl"), "wb") as f:
                pickle.dump({"model": model, "y_scaler": None}, f)
=======
            with open(MODEL_DIR / f"{key}.pkl", "wb") as f:
                pickle.dump(model, f)
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2  = r2_score(y_test, y_pred)

        results.append({
            "Model": label,
            "MSE": round(mse, 3),
            "RMSE": round(rmse, 3),
            "MAE": round(mae, 3),
<<<<<<< HEAD
            "R²": round(r2, 3),
=======
            "R²": round(r2, 3)
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
        })

    return pd.DataFrame(results)