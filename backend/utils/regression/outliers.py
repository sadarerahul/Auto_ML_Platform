import os
import pandas as pd
import numpy as np

# Define path to cleaned data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../../../frontend")
UPLOAD_DIR = os.path.join(FRONTEND_DIR, "static/uploads")
DATA_PATH = os.path.join(UPLOAD_DIR, "cleaned_data.csv")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 🔢 Get numeric columns
def get_numeric_columns_for_outliers():
    try:
        df = pd.read_csv(DATA_PATH)
        return df.select_dtypes(include=["number"]).columns.tolist()
    except Exception:
        return []


# 🧮 Outlier Handling Methods
def handle_outliers(column: str, method: str):
    try:
        df = pd.read_csv(DATA_PATH)

        if column not in df.columns:
            return None, None, f"❌ Column '{column}' not found."

        # Summary before
        summary_before = df[column].describe().to_frame(name="Before")

        if method == "iqr":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()
            df = df[np.abs((df[column] - mean) / std) <= 3]

        elif method == "capping":
            lower_cap = df[column].quantile(0.05)
            upper_cap = df[column].quantile(0.95)
            df[column] = np.where(df[column] < lower_cap, lower_cap, df[column])
            df[column] = np.where(df[column] > upper_cap, upper_cap, df[column])

        else:
            return None, None, f"❌ Unknown outlier method: {method}"

        # Summary after
        summary_after = df[column].describe().to_frame(name="After")

        # Save back to disk
        df.to_csv(DATA_PATH, index=False)

        return summary_before.to_html(classes="table table-bordered table-sm"), \
               summary_after.to_html(classes="table table-bordered table-sm"), \
               f"✅ Outlier handling applied using method: {method.upper()}"

    except Exception as e:
        return None, None, f"❌ Error handling outliers: {str(e)}"
