import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from .cleaning import load_data
from .selection_state import load_xy
from backend.utils.regression.session_state import get_active_dataset
import os

# 📁 Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
os.makedirs(SPLIT_DIR, exist_ok=True)

def perform_split(test_size: float, random_state: int, preview_rows: int = 5):
    """Perform a train-test split and save dataset-prefixed splits for cleanup support."""
    xy = load_xy()
    if not xy["X"] or not xy["y"]:
        raise ValueError("Please define X / y first in Feature‑Selection.")

    df = load_data()
    X = df[xy["X"]]
    y = df[xy["y"]]

    if len(X) < 10:
        raise ValueError("Not enough data to split. Please check your selections.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # 💾 Save with dataset prefix for cleanup
    dataset_name = get_active_dataset()
    base = Path(dataset_name).stem

    pd.DataFrame(X_train).to_csv(os.path.join(SPLIT_DIR, f"{base}_X_train.csv"), index=False)
    pd.DataFrame(X_test).to_csv(os.path.join(SPLIT_DIR, f"{base}_X_test.csv"), index=False)
    pd.DataFrame(y_train).to_csv(os.path.join(SPLIT_DIR, f"{base}_y_train.csv"), index=False, header=True)
    pd.DataFrame(y_test).to_csv(os.path.join(SPLIT_DIR, f"{base}_y_test.csv"), index=False, header=True)

    return {
        "X_train": X_train.head(preview_rows),
        "X_test": X_test.head(preview_rows),
        "y_train": y_train.head(preview_rows).to_frame(name=y.name or "y"),
        "y_test": y_test.head(preview_rows).to_frame(name=y.name or "y"),
        "shapes": {
            "X_train": X_train.shape,
            "X_test": X_test.shape,
            "y_train": y_train.shape,
            "y_test": y_test.shape,
        }
    }