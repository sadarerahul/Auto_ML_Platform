import os
from backend.config import UPLOAD_DIR

# Ensure the upload directory exists at module load
os.makedirs(UPLOAD_DIR, exist_ok=True)

def list_csv_files():
    """
    Return all CSV files in uploads/ except canonical 'uploaded_data.csv',
    sorted by modification time (most recent first).
    """
    csvs = [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv") and f != "uploaded_data.csv"
    ]
    return sorted(
        csvs,
        key=lambda f: os.path.getmtime(os.path.join(UPLOAD_DIR, f)),
        reverse=True
    )

def save_raw_copy(upload_file, unique_name: str):
    """
    Write raw bytes of the upload to uploads/ using the given unique file name.
    """
    full_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(full_path, "wb") as f:
        f.write(upload_file.file.read())

def delete_files(filenames: list[str]):
    """
    Delete given filenames from the uploads/ directory if they exist.
    """
    for fname in filenames:
        path = os.path.join(UPLOAD_DIR, fname)
        if os.path.exists(path):
            os.remove(path)