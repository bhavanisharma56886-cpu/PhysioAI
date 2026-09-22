import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# 1. FIND PROJECT FOLDER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# 2. DATASET PATHS
# ============================================================

GOOD_DATA = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "features"
    / "batch_good_data.csv"
)

BAD_DATA = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "features"
    / "batch_bad_data.csv"
)


# ============================================================
# 3. MODEL PATH
# ============================================================

MODEL_PATH = (
    PROJECT_ROOT
    / "ai"
    / "ml"
    / "models"
    / "bicep_form_model.pkl"
)


# ============================================================
# 4. LOAD DATASET
# ============================================================

print("\nLoading dataset...")

good_df = pd.read_csv(GOOD_DATA)
bad_df = pd.read_csv(BAD_DATA)

df = pd.concat(
    [good_df, bad_df],
    ignore_index=True
)

print("Total samples:", len(df))


# ============================================================
# 5. SEPARATE FEATURES AND LABEL
# ============================================================

X = df.drop(columns=["label"])
y = df["label"]


# ============================================================
# 6. CREATE SAME TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# 7. LOAD SAVED MODEL
# ============================================================

package = joblib.load(MODEL_PATH)

model = package["model"]


# ============================================================
# 8. MAKE PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 9. CALCULATE METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

cm = confusion_matrix(
    y_test,
    y_pred
)


# ============================================================
# 10. DISPLAY RESULTS
# ============================================================

print("\n")
print("==============================================")
print("        BICEP CURL MODEL EVALUATION")
print("==============================================")

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


print("\n----------------------------------------------")
print("CONFUSION MATRIX")
print("----------------------------------------------")

print(cm)


print("\n----------------------------------------------")
print("CLASSIFICATION REPORT")
print("----------------------------------------------")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "BAD FORM",
            "GOOD FORM"
        ],
        zero_division=0
    )
)


print("==============================================")
print("Evaluation completed successfully.")
print("==============================================")