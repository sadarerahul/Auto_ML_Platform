import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from .cleaning import load_data
from .selection_state import load_xy
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/uploads"))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
os.makedirs(SPLIT_DIR, exist_ok=True)


def perform_split(test_size: float, random_state: int, preview_rows: int = 5):
    """Perform a train-test split and save preview CSVs — regression mode only."""
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

    # Save splits
    X_train.to_csv(os.path.join(SPLIT_DIR, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(SPLIT_DIR, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(SPLIT_DIR, "y_train.csv"), index=False, header=True)
    y_test.to_csv(os.path.join(SPLIT_DIR, "y_test.csv"), index=False,header=True)
    # Previews
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