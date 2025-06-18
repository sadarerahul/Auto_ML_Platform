import os
import pandas as pd

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "../../../frontend/static/uploads")
DATA_PATH = os.path.join(UPLOAD_DIR, "uploaded_data.csv")
CLEANED_DATA_PATH = os.path.join(UPLOAD_DIR, "cleaned_data.csv")

# Ensure upload folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔄 Load data (auto-load cleaned if exists)
def load_data():
    """Return the freshest available DataFrame.
    • If cleaned_data.csv exists **and** is newer than uploaded_data.csv → use it
    • Otherwise fall back to uploaded_data.csv
    """
    if os.path.exists(CLEANED_DATA_PATH) and os.path.exists(DATA_PATH):
        if os.path.getmtime(CLEANED_DATA_PATH) >= os.path.getmtime(DATA_PATH):
            return pd.read_csv(CLEANED_DATA_PATH)
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()

# 📦 Save cleaned data
def save_data(df):
    df.to_csv(CLEANED_DATA_PATH, index=False)

# 🧼 Get columns with missing values
def get_missing_columns():
    df = load_data()
    return df.columns[df.isnull().any()].tolist()

# 📈 Get categorical columns
def get_categorical_columns():
    df = load_data()
    return df.select_dtypes(include="object").columns.tolist()

# ✅ Apply missing value treatment
def apply_missing_value_strategy(column, strategy, custom_value=None):
    df = load_data()
    if column not in df.columns:
        return False, f"⚠️ Column '{column}' not found."

    if strategy == "drop":
        df = df.dropna(subset=[column])
        msg = f"🗑️ Dropped rows where '{column}' is missing."
    elif strategy == "mean":
        mean_val = df[column].mean()
        df[column] = df[column].fillna(mean_val)
        msg = f"📊 Filled missing '{column}' with mean: {mean_val:.2f}"
    elif strategy == "median":
        median_val = df[column].median()
        df[column] = df[column].fillna(median_val)
        msg = f"📐 Filled missing '{column}' with median: {median_val:.2f}"
    elif strategy == "mode":
        mode_val = df[column].mode()[0]
        df[column] = df[column].fillna(mode_val)
        msg = f"🎯 Filled missing '{column}' with mode: {mode_val}"
    elif strategy == "custom" and custom_value is not None:
        df[column] = df[column].fillna(custom_value)
        msg = f"✍️ Filled missing '{column}' with custom value: {custom_value}"
    else:
        return False, "❌ Invalid strategy or missing custom value."

    save_data(df)
    return True, msg

# 🔠 Apply encoding strategy
def apply_encoding(column, encoding_type):
    df = load_data()

    if column not in df.columns:
        return False, f"⚠️ Column '{column}' not found."

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

# 📋 Return summary of cleaned data (used for preview)
def get_cleaned_data_preview(n=10):
    df = load_data()
    return df.head(n).to_html(classes="table table-sm table-bordered", index=False)
