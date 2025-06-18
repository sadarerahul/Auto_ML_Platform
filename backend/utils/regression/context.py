# backend/utils/regression/context.py
from backend.services import dataset_service
from backend.config import MAX_DATASETS

def get_sidebar_context(active_file="uploaded_data.csv"):
    files = dataset_service.list_files()
    return {
        "files": files,
        "max_datasets": MAX_DATASETS,
        "show_delete": len(files) >= MAX_DATASETS,
        "active_file": active_file or (files[-1] if files else None)
    }
