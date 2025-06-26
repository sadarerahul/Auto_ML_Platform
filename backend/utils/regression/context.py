import os
from backend.services import dataset_service
from backend.config import MAX_DATASETS
from .session_state import get_active_dataset, set_active_dataset

def get_sidebar_context(active_file=None, step=1):
    # Only show raw datasets (not *_cleaned.csv)
    all_files = dataset_service.list_files()
    raw_files = [f for f in all_files if not f.endswith("_cleaned.csv")]

    active = active_file or get_active_dataset()

    return {
        "files": raw_files,
        "max_datasets": MAX_DATASETS,
        "show_delete": len(raw_files) >= MAX_DATASETS,
        "active_file": os.path.basename(active) if active else "",
        "workflow_step": step,  # ✅ Added to track flowline
    }
