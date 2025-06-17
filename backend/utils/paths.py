import os

# Folder: utils/paths.py
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR   = os.path.join(BASE_DIR, "../../frontend/static/uploads")
DATA_PATH    = os.path.join(UPLOAD_DIR, "uploaded_data.csv")

# Ensure the folder exists at import time
os.makedirs(UPLOAD_DIR, exist_ok=True)
