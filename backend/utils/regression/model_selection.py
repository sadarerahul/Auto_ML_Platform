"""
Train and evaluate multiple regression models,
then store the trained model(s) as pickles in frontend/static/models/.
"""

from pathlib import Path
import pickle
import numpy as np
import pandas as pd

from sklearn.linear_model   import LinearRegression
from sklearn.tree           import DecisionTreeRegressor
from sklearn.ensemble       import RandomForestRegressor
from sklearn.svm            import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing  import StandardScaler
from sklearn.metrics        import mean_squared_error, mean_absolute_error, r2_score

# ── folders ────────────────────────────────────────────────────────────
SPLIT_DIR = Path("frontend/static/splits")
MODEL_DIR = Path("frontend/static/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ── helpers ────────────────────────────────────────────────────────────
def _load(name: str) -> pd.DataFrame:
    fp = SPLIT_DIR / f"{name}.csv"
    if not fp.exists():
        raise FileNotFoundError(f"{fp.name} not found – run previous steps.")
    return pd.read_csv(fp)

def available_models() -> dict[str, tuple[str, object]]:
    """Return dict key → (readable label, sklearn instance)."""
    return {
        "linear": ("Linear Regression",
                   LinearRegression()),
        "dtr":    ("Decision Tree",
                   DecisionTreeRegressor(random_state=42)),
        "rf":     ("Random Forest",
                   RandomForestRegressor(n_estimators=100, random_state=42)),
        "svr":    ("Support Vector Regression",
                   SVR(kernel="rbf")),
        "mlp":    ("Neural Network (MLP)",
                   MLPRegressor(hidden_layer_sizes=(128, 64, 32),
                                activation="relu",
                                solver="adam",
                                learning_rate_init=0.001,
                                max_iter=1000,
                                random_state=42)),
    }

# ── main routine ───────────────────────────────────────────────────────
def train_and_evaluate(model_keys: list[str]) -> pd.DataFrame:
    """Train chosen models, save pickles, and return metrics table."""
    X_train = _load("X_train_scaled")
    X_test  = _load("X_test_scaled")
    y_train = _load("y_train").squeeze()
    y_test  = _load("y_test").squeeze()

    results: list[dict[str, float | str]] = []

    for key in model_keys:
        label, model = available_models()[key]

        # SVR needs target scaling
        if key == "svr":
            y_scaler = StandardScaler()
            y_train_scaled = y_scaler.fit_transform(
                y_train.to_numpy().reshape(-1, 1)
            ).ravel()

            model.fit(X_train, y_train_scaled)
            y_pred_scaled = model.predict(X_test).reshape(-1, 1)
            y_pred = y_scaler.inverse_transform(y_pred_scaled).ravel()

            with (MODEL_DIR / f"{key}.pkl").open("wb") as f:
                pickle.dump({"model": model, "y_scaler": y_scaler}, f)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            with (MODEL_DIR / f"{key}.pkl").open("wb") as f:
                pickle.dump(model, f)

        mse  = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae  = mean_absolute_error(y_test, y_pred)
        r2   = r2_score(y_test, y_pred)

        results.append({
            "Model": label,
            "MSE":   round(mse,  3),
            "RMSE":  round(rmse, 3),
            "MAE":   round(mae,  3),
            "R²":    round(r2,   3)
        })

    return pd.DataFrame(results)
