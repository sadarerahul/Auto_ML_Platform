import os

# Define base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/uploads"))
CLEANED_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../frontend/static/cleaned"))
ACTIVE_DATASET_PATH = os.path.join(UPLOAD_DIR, "active_dataset.txt")  # stores filename only
# ✅ New: Manage processing (cleaned) dataset for backend use
PROCESSING_DATASET_PATH = os.path.abspath(os.path.join(CLEANED_DIR, "processing_dataset.txt"))

# 🔹 Get the currently active dataset (just the file name)
def get_active_dataset():
    if os.path.exists(ACTIVE_DATASET_PATH):
        dataset_name = open(ACTIVE_DATASET_PATH, encoding="utf-8").read().strip()
        if os.path.exists(os.path.join(UPLOAD_DIR, dataset_name)):
            return dataset_name
        else:
            os.remove(ACTIVE_DATASET_PATH)
    return ""




# 🔹 Get full path to raw/original dataset (for UI preview)
def get_active_dataset_path():
    dataset_name = get_active_dataset()
    if dataset_name:
        full_path = os.path.join(UPLOAD_DIR, dataset_name)
        if os.path.exists(full_path):
            return full_path
    return ""

# 🔹 Get full path to cleaned version (for backend processing)
def get_cleaned_dataset_path():
    dataset_name = get_active_dataset()
    if dataset_name:
        base = os.path.splitext(dataset_name)[0]
        cleaned_name = f"{base}_cleaned.csv"
        cleaned_path = os.path.join(CLEANED_DIR, cleaned_name)
        if os.path.exists(cleaned_path):
            return cleaned_path
    return ""

# 🔹 Set the currently active dataset (raw/original only)
def set_active_dataset(filename):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(ACTIVE_DATASET_PATH, "w", encoding="utf-8") as f:
        f.write(os.path.basename(filename).strip())

# 🔹 Check if a given dataset is currently active
def is_dataset_active(filename):
    return os.path.basename(filename) == get_active_dataset()

# 🔹 Clear the active dataset reference
def clear_active_dataset():
    if os.path.exists(ACTIVE_DATASET_PATH):
        os.remove(ACTIVE_DATASET_PATH)


def set_processing_dataset(filename):
    with open(PROCESSING_DATASET_PATH, "w", encoding="utf-8") as f:
        f.write(os.path.basename(filename).strip())

def get_processing_dataset_path():
    if os.path.exists(PROCESSING_DATASET_PATH):
        dataset_name = open(PROCESSING_DATASET_PATH, encoding="utf-8").read().strip()
        path = os.path.join(CLEANED_DIR, dataset_name)
        if os.path.exists(path):
            return path
    return get_active_dataset_path()  # fallback to raw
