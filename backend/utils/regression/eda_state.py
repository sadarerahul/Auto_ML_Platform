# backend/utils/regression/eda_state.py
import json
import os
import tempfile
from typing import Dict, Optional

STATE_FILE = "frontend/static/eda_state.json"


# ─────────────────────────────────────────────
# Internal Helpers
# ─────────────────────────────────────────────
def load_eda_state() -> Dict:
    """Load EDA state from JSON file."""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def atomic_save(data: Dict):
    """Safely write JSON to file using atomic operation."""
    tmp_file = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
    json.dump(data, tmp_file)
    tmp_file.flush()
    tmp_file.close()
    os.replace(tmp_file.name, STATE_FILE)


# ─────────────────────────────────────────────
# Public Functions
# ─────────────────────────────────────────────
def save_eda_state(state: Dict):
    """Save EDA state to JSON file."""
    atomic_save(state)


def clear_eda_state():
    """Remove the entire EDA state file."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def clear_dataset_state(dataset: str):
    """Clear EDA state for a specific dataset."""
    state = load_eda_state()
    if dataset in state:
        del state[dataset]
        save_eda_state(state)


def get_eda_results(dataset: str) -> Optional[Dict]:
    """Get saved EDA results for a specific dataset."""
    return load_eda_state().get(dataset)


def update_eda_results(dataset: str, key: str, value):
    """Update EDA results for a specific dataset."""
    state = load_eda_state()
    if dataset not in state:
        state[dataset] = {}
    state[dataset][key] = value
    save_eda_state(state)
