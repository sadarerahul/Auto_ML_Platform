import json
import os
from typing import Dict, Optional

# State file for storing visualization settings/results
STATE_FILE = "frontend/static/visualize_state.json"


def load_visualize_state() -> Dict:
    """Load Visualization state from JSON file."""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_visualize_state(state: Dict):
    """Save Visualization state to JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def clear_visualize_state():
    """Remove Visualization state file."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def get_visualize_results(dataset: str) -> Optional[Dict]:
    """Get saved visualization results for a specific dataset."""
    return load_visualize_state().get(dataset)


def update_visualize_results(dataset: str, key: str, value):
    """Update visualization results for a specific dataset."""
    state = load_visualize_state()
    if dataset not in state:
        state[dataset] = {}
    state[dataset][key] = value
    save_visualize_state(state)
