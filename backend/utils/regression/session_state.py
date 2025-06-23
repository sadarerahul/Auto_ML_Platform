from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = (BASE_DIR / "../../../frontend/static/uploads").resolve()
ACTIVE_DATASET_PATH = UPLOAD_DIR / "active_dataset.txt"

# 🔹 Get the currently active dataset
def get_active_dataset() -> str:
    if ACTIVE_DATASET_PATH.exists():
        return ACTIVE_DATASET_PATH.read_text(encoding="utf-8").strip()
    return ""  # No dataset selected yet

# 🔹 Set the currently active dataset
def set_active_dataset(filename: str) -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure path exists
    ACTIVE_DATASET_PATH.write_text(filename.strip(), encoding="utf-8")

# 🔹 Optional: Check if a dataset is active
def is_dataset_active(filename: str) -> bool:
    return filename.strip() == get_active_dataset()