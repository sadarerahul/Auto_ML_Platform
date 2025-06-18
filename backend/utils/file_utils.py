import os
from backend.config import UPLOAD_DIR

os.makedirs(UPLOAD_DIR, exist_ok=True)

def list_csv_files():
    """Return all CSV files in uploads/ except canonical 'uploaded_data.csv'."""
    return [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv") and f != "uploaded_data.csv"
    ]

def save_raw_copy(upload_file, unique_name: str):
    """Write raw bytes of the upload to uploads/."""
    with open(os.path.join(UPLOAD_DIR, unique_name), "wb") as f:
        f.write(upload_file.file.read())

def delete_files(filenames: list[str]):
    for fname in filenames:
        path = os.path.join(UPLOAD_DIR, fname)
        if os.path.exists(path):
            os.remove(path)
