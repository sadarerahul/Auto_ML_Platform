import os
import pandas as pd
from backend.utils.regression.session_state import get_active_dataset, set_active_dataset

# 📁 Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "../../../frontend/static/uploads")
CLEANED_DATA_DIR = os.path.join(BASE_DIR, "../../../frontend/static/cleaned")
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)

# 🔧 Resolve paths to raw and cleaned versions
def _get_data_paths():
    filename = get_active_dataset()
    if not filename:
        return None, None
    original_path = os.path.join(UPLOAD_DIR, filename)
    cleaned_name = filename.replace(".csv", "_cleaned.csv")
    cleaned_path = os.path.join(CLEANED_DATA_DIR, cleaned_name)
    return original_path, cleaned_path

# 🔄 Load the dataset (prefers cleaned version if available)
def load_data():
    original_path, cleaned_path = _get_data_paths()
    if not original_path:
        return pd.DataFrame()

    if os.path.exists(cleaned_path):
        return pd.read_csv(cleaned_path)

    if os.path.exists(original_path):
        return pd.read_csv(original_path)

    return pd.DataFrame()

# 💾 Save cleaned data securely & activate it
def save_data(df: pd.DataFrame):
    _, cleaned_path = _get_data_paths()
    if cleaned_path:
        df.head(500).to_csv(cleaned_path, index=False)
        cleaned_name = os.path.basename(cleaned_path)
        set_active_dataset(cleaned_name)  # ✅ Make cleaned file active

# ❓ Get columns with missing values
def get_missing_columns():
    df = load_data()
    return df.columns[df.isnull().any()].tolist()

# 🔤 Detect categorical columns
def get_categorical_columns():
    df = load_data()
    return df.select_dtypes(include="object").columns.tolist()

# 🩹 Apply missing value strategy
def apply_missing_value_strategy(column, strategy, custom_value=None):
    df = load_data()

    if column not in df.columns:
        return False, f"⚠️ Column '{column}' not found."
    if df[column].isnull().all():
        return False, f"⚠️ Cannot fill '{column}' — all values are missing."

    try:
        if strategy == "drop":
            df = df.dropna(subset=[column])
            msg = f"🗑️ Dropped rows where '{column}' is missing."
        elif strategy == "mean":
            value = df[column].mean()
            df[column] = df[column].fillna(value)
            msg = f"📊 Filled missing '{column}' with mean: {value:.2f}"
        elif strategy == "median":
            value = df[column].median()
            df[column] = df[column].fillna(value)
            msg = f"📐 Filled missing '{column}' with median: {value:.2f}"
        elif strategy == "mode":
            value = df[column].mode()[0]
            df[column] = df[column].fillna(value)
            msg = f"🎯 Filled missing '{column}' with mode: {value}"
        elif strategy == "custom" and custom_value is not None:
            df[column] = df[column].fillna(custom_value)
            msg = f"✍️ Filled missing '{column}' with custom value: {custom_value}"
        else:
            return False, "❌ Invalid strategy or missing custom value."

        save_data(df)
        return True, msg

    except Exception as e:
        return False, f"❌ Error applying strategy: {e}"

# 🧠 Apply encoding to categorical column
def apply_encoding(column, encoding_type):
    df = load_data()

    if column not in df.columns:
        return False, f"⚠️ Column '{column}' not found."

    try:
        if encoding_type == "label":
            df[column] = df[column].astype("category").cat.codes
            msg = f"🔢 Applied label encoding to '{column}'"
        elif encoding_type == "onehot":
            onehot_df = pd.get_dummies(df[column], prefix=column)
            df = pd.concat([df.drop(columns=[column]), onehot_df], axis=1)
            msg = f"🌈 Applied one-hot encoding to '{column}'"
        elif encoding_type == "frequency":
            freq_map = df[column].value_counts().to_dict()
            df[column] = df[column].map(freq_map)
            msg = f"📊 Applied frequency encoding to '{column}'"
        else:
            return False, "❌ Invalid encoding type."

        save_data(df)
        return True, msg

    except Exception as e:
        return False, f"❌ Error during encoding: {e}"

# 🔍 Preview cleaned data (for display)
def get_cleaned_data_preview(n=10):
    df = load_data()
    if df.empty:
        return "<p class='text-warning mb-0'>⚠️ No data available to preview.</p>"
    return f"<p class='text-success mb-2'>✅ Showing cleaned data preview:</p>" + \
           df.head(n).to_html(classes="table table-sm table-bordered", index=False)
