# Stores / loads user‑chosen X (predictors) and y (target)

import json, os
from pathlib import Path

STATE_FILE = Path("frontend/static/xy_selection.json")

def save_xy(x_cols: list[str], y_col: str) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"X": x_cols, "y": y_col}, f, indent=2)

def load_xy() -> dict:
    if not STATE_FILE.exists():
        return {"X": [], "y": None}
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)
