import pandas as pd
import numpy as np
import os
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import GroupShuffleSplit


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = r"C:\Users\hp\Desktop\AI-Physiotherapy\data\raw\features\squat_features.csv"

MODEL_FILE = r"C:\Users\hp\Desktop\AI-Physiotherapy\ai\ml\models\squat_form_model.pkl"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("SQUAT FORM MODEL TRAINING")
print("=" * 60)

print("\nLoading feature dataset...")

df = pd.read_csv(INPUT_FILE)

print("Dataset shape:", df.shape)


# ============================================================
# LABEL
# ============================================================

# True  -> GOOD
# False -> BAD

df["label"] = df["is_correct"].astype(int)


# ============================================================
# FEATURES
# ============================================================

# These columns identify the repetition/person.
# They must NOT be given to the ML model.

columns_to_remove = [
    "is_correct",
    "label",
    "subject_id",
    "repetition"
]

X = df.drop(
    columns=columns_to_remove
)

y = df["label"]

groups = df["subject_id"]


print("\nNumber of ML features:", X.shape[1])

print("Good repetitions:", (y == 1).sum())
print("Bad repetitions:", (y == 0).sum())


# ============================================================
# TRAIN / TEST SPLIT BY SUBJECT
# ============================================================

print("\nCreating subject-based train/test split...")

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.25,
    random_state=42
)

train_indices, test_indices = next(
    splitter.split(
        X,
        y,
        groups=groups
    )
)

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]

train_subjects = groups.iloc[train_indices].unique()
test_subjects = groups.iloc[test_indices].unique()


print("\nTraining subjects:")
print(list(train_subjects))

print("\nTesting subjects:")
print(list(test_subjects))

print("\nTraining repetitions:", len(X_train))
print("Testing repetitions:", len(X_test))


# ============================================================
# RANDOM FOREST
# ============================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    max_features="sqrt",
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

print("✅ Model training complete!")


# ============================================================
# PREDICTION
# ============================================================

print("\nTesting model...")

y_pred = model.predict(X_test)


# ============================================================
# ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n" + "=" * 60)
print("MODEL RESULTS")
print("=" * 60)

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print(
    f"Accuracy percentage: {accuracy * 100:.2f}%"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n--- CLASSIFICATION REPORT ---")

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


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("--- CONFUSION MATRIX ---")

cm = confusion_matrix(
    y_test,
    y_pred
)

print(cm)

print("\nMatrix meaning:")
print("[[BAD predicted BAD, BAD predicted GOOD]")
print(" [GOOD predicted BAD, GOOD predicted GOOD]]")


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n--- TOP FEATURES ---")

importance = pd.Series(
    model.feature_importances_,
    index=X.columns
)

importance = importance.sort_values(
    ascending=False
)

print(
    importance.head(15)
)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    os.path.dirname(MODEL_FILE),
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_FILE
)

print("\n" + "=" * 60)

print("✅ MODEL SAVED")

print(MODEL_FILE)

print("=" * 60)