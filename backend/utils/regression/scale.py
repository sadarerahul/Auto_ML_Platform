import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler

SPLIT_DIR = Path("frontend/static/splits")
SPLIT_DIR.mkdir(parents=True, exist_ok=True)

def _load_split(name: str) -> pd.DataFrame:
    path = SPLIT_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path.name} not found. Run Train‑Test Split first.")
    return pd.read_csv(path)

def apply_scaler(scaler_type: str):
    X_train = _load_split("X_train")
    X_test  = _load_split("X_test")

    if scaler_type == "standard":
        scaler = StandardScaler()
    elif scaler_type == "minmax":
        scaler = MinMaxScaler(feature_range=(0, 1))
    else:
        raise ValueError("Scaler type must be 'standard' or 'minmax'.")

    # Fit on train, transform both
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train),
                                  columns=X_train.columns)
    X_test_scaled  = pd.DataFrame(scaler.transform(X_test),
                                  columns=X_test.columns)

    # Save
    X_train_scaled.to_csv(SPLIT_DIR / "X_train_scaled.csv", index=False)
    X_test_scaled.to_csv(SPLIT_DIR / "X_test_scaled.csv",  index=False)

    preview = {
        "X_train_scaled": X_train_scaled.head(5),
        "X_test_scaled":  X_test_scaled.head(5),
    }
    return preview
