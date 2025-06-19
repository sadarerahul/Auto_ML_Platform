import os, pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path
from .cleaning import load_data                       # freshest dataset
from .selection_state import load_xy                  # current X / y

SPLIT_DIR = Path("frontend/static/splits")
SPLIT_DIR.mkdir(parents=True, exist_ok=True)

def perform_split(test_size: float, random_state: int):
    xy = load_xy()
    if not xy["X"] or not xy["y"]:
        raise ValueError("Please define X / y first in Feature‑Selection.")
    
    df = load_data()
    X = df[xy["X"]]
    y = df[xy["y"]]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # save CSVs for next steps
    X_train.to_csv(SPLIT_DIR / "X_train.csv", index=False)
    X_test.to_csv(SPLIT_DIR / "X_test.csv",  index=False)
    y_train.to_csv(SPLIT_DIR / "y_train.csv", index=False, header=True)
    y_test.to_csv(SPLIT_DIR / "y_test.csv",  index=False, header=True)
    
    # return small previews
    preview = {
        "X_train": X_train.head(5),
        "X_test":  X_test.head(5),
        # convert Series → DataFrame so .to_html exists
        "y_train": y_train.head(5).to_frame(name=y.name or "y"),
        "y_test":  y_test.head(5).to_frame(name=y.name or "y"),
    }
    return preview
