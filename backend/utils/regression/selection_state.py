<<<<<<< HEAD
"""
Persist / retrieve the user-chosen predictor columns (X) and target (y).
Safe against earlier “directory named .json” mistake.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

# ── Locate files and folders ──────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent            # backend/utils/regression
ROOT_DIR   = BASE_DIR.parent.parent.parent              # project root
STATIC_DIR = ROOT_DIR / "frontend/static"
UPLOAD_DIR = STATIC_DIR / "uploads"
STATE_FILE = STATIC_DIR / "xy_selection.json"           # <-- file, not dir!

# Ensure parent directory exists (creates …/static if missing)
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

# If a directory with this name was created by mistake, remove it
if STATE_FILE.exists() and STATE_FILE.is_dir():
    # remove empty dir; or rmdir(dir, ignore_errors=True) if needed
    STATE_FILE.rmdir()

# ── Public helpers ───────────────────────────────────────────────────
def save_xy(x_cols: List[str], y_col: str) -> None:
    """Save selected predictor list and target column."""
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump({"X": x_cols, "y": y_col}, f, indent=2)


def load_xy() -> Dict[str, Any]:
    """Return {"X": [...], "y": "..."} or defaults if file missing."""
    if not STATE_FILE.is_file():
        return {"X": [], "y": None}
    with STATE_FILE.open(encoding="utf-8") as f:
        return json.load(f)
=======
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
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
