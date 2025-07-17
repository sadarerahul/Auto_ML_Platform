import os
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split , KFold

from .cleaning import load_data
from .selection_state import load_xy
from backend.utils.regression.session_state import get_active_dataset

# 📁 Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/splits"))
os.makedirs(SPLIT_DIR, exist_ok=True)


def perform_split(test_size: float, random_state: int, preview_rows: int = 5) -> dict:
    """
    Perform a train-test split and save split CSVs for the current dataset.

    Parameters
    ----------
    test_size : float
        Proportion of the dataset to include in the test split.
    random_state : int
        Seed for reproducibility.
    preview_rows : int
        Number of preview rows to return from each split.

    Returns
    -------
    dict
        Dictionary with split previews and their shapes.
    """
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

    # 💾 Save with dataset prefix
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

def perform_sequential_split(test_size: float, preview_rows: int = 5) -> dict:
    xy = load_xy()
    if not xy["X"] or not xy["y"]:
        raise ValueError("Please define X / y first in Feature‑Selection.")

    df = load_data()
    X = df[xy["X"]]
    y = df[xy["y"]]

    n = len(X)
    if n < 10:
        raise ValueError("Not enough data to split.")

    split_index = int(n * (1 - test_size))

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

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
# def perform_kfold_split(n_splits: int = 5, random_state: int = 42, preview_rows: int = 5) -> dict:
#     # Load selected features and target
#     xy = load_xy()
#     if not xy.get("X") or not xy.get("y"):
#         raise ValueError("❌ Please define X and y first in Feature Selection.")

#     # Load dataset
#     df = load_data()
#     X = df[xy["X"]]
#     y = df[xy["y"]]

#     # Initialize KFold splitter
#     kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
#     previews = []

#     for fold, (train_idx, test_idx) in enumerate(kf.split(X), start=1):
#         x_train, x_test = X.iloc[train_idx], X.iloc[test_idx]
#         y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

#         # Append preview of each fold
#         previews.append({
#     "fold": fold,
#     "X_train": x_train.head(preview_rows),
#     "X_test": x_test.head(preview_rows),
#     "y_train": y_train.head(preview_rows).to_frame(name="y_train"),
#     "y_test": y_test.head(preview_rows).to_frame(name="y_test"),
#     "shapes": {
#         "X_train": x_train.shape,
#         "X_test": x_test.shape,
#         "y_train": y_train.shape,
#         "y_test": y_test.shape,
#     }
# })


#     return {
#         "n_splits": n_splits,
#         "preview_rows": preview_rows,
#         "kfold": previews
#     }