import os
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ============================================================
# PATHS
# ============================================================

BASE_DIR = r"C:\Users\hp\Desktop\AI-Physiotherapy"

FEATURE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "features",
    "squat_features.csv"
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "ai",
    "ml",
    "models",
    "squat_form_model_normalized.pkl"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("NORMALIZED SQUAT MODEL TRAINING")
print("=" * 60)

print("\nLoading squat feature dataset...")

df = pd.read_csv(FEATURE_FILE)

print("Dataset shape:", df.shape)


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\nLabels:")

print(
    "GOOD FORM:",
    int(df["is_correct"].sum())
)

print(
    "BAD FORM:",
    int((~df["is_correct"]).sum())
)


# ============================================================
# CREATE NORMALIZED FEATURES
# ============================================================

print("\nCreating normalized squat features...")


def safe_divide(a, b):
    """
    Divide safely.
    If denominator is zero, return 0.
    """
    return np.where(
        np.abs(b) > 1e-8,
        a / b,
        0
    )


# ------------------------------------------------------------
# We mainly keep:
# - angles
# - normalized distances
# - movement/velocity information
# - depth information
# ------------------------------------------------------------

feature_columns = []


# ============================================================
# ANGLE FEATURES
# ============================================================

angle_keywords = [
    "knee_angle",
    "hip_angle",
    "torso_angle"
]

for column in df.columns:

    if any(keyword in column for keyword in angle_keywords):

        if column not in feature_columns:
            feature_columns.append(column)


# ============================================================
# SYMMETRY FEATURES
# ============================================================

for column in df.columns:

    if "symmetry" in column:

        if column not in feature_columns:
            feature_columns.append(column)


# ============================================================
# NORMALIZED DISTANCE FEATURES
# ============================================================

distance_columns = [
    "knee_distance_mean",
    "knee_distance_std",
    "knee_distance_min",
    "knee_distance_max",
    "knee_distance_range",

    "hip_distance_mean",
    "hip_distance_std",
    "hip_distance_min",
    "hip_distance_max",
    "hip_distance_range",

    "ankle_distance_mean",
    "ankle_distance_std",
    "ankle_distance_min",
    "ankle_distance_max",
    "ankle_distance_range"
]

for column in distance_columns:

    if column in df.columns:

        # Find corresponding hip distance mean
        if "hip_distance_mean" in df.columns:

            normalized_name = column + "_normalized"

            if column == "hip_distance_mean":
                continue

            df[normalized_name] = safe_divide(
                df[column],
                df["hip_distance_mean"]
            )

            feature_columns.append(normalized_name)


# ============================================================
# KNEE / ANKLE HORIZONTAL FEATURES
# ============================================================

for column in df.columns:

    if "knee_ankle_horizontal" in column:

        normalized_name = column + "_normalized"

        df[normalized_name] = safe_divide(
            df[column],
            df["hip_distance_mean"]
        )

        feature_columns.append(normalized_name)


# ============================================================
# VERTICAL POSITION FEATURES
# ============================================================

vertical_keywords = [
    "knee_vertical",
    "hip_vertical",
    "torso_vertical"
]

for column in df.columns:

    if any(keyword in column for keyword in vertical_keywords):

        if column.endswith("_normalized"):
            continue

        normalized_name = column + "_normalized"

        if "hip_distance_mean" in df.columns:

            df[normalized_name] = safe_divide(
                df[column],
                df["hip_distance_mean"]
            )

            feature_columns.append(normalized_name)


# ============================================================
# VELOCITY FEATURES
# ============================================================

for column in df.columns:

    if "velocity" in column:

        if column not in feature_columns:

            feature_columns.append(column)


# ============================================================
# DEPTH FEATURES
# ============================================================

for column in df.columns:

    if "depth" in column:

        if column not in feature_columns:

            feature_columns.append(column)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

feature_columns = list(dict.fromkeys(feature_columns))


# ============================================================
# REMOVE INVALID COLUMNS
# ============================================================

feature_columns = [
    column
    for column in feature_columns
    if column in df.columns
]


print(
    "\nNumber of selected features:",
    len(feature_columns)
)


# ============================================================
# CREATE X AND Y
# ============================================================

X = df[feature_columns].copy()

y = df["is_correct"].astype(int)

groups = df["subject_id"]


# ============================================================
# CLEAN DATA
# ============================================================

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.fillna(0)


# ============================================================
# GROUP K-FOLD CROSS VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("3-FOLD SUBJECT-BASED CROSS VALIDATION")
print("=" * 60)

group_kfold = GroupKFold(n_splits=3)

fold_scores = []

fold_number = 1


for train_index, test_index in group_kfold.split(
    X,
    y,
    groups
):

    print("\n" + "-" * 60)

    print("FOLD", fold_number)

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = y.iloc[train_index]
    y_test = y.iloc[test_index]

    groups_train = groups.iloc[train_index]
    groups_test = groups.iloc[test_index]


    print(
        "Training subjects:",
        sorted(groups_train.unique())
    )

    print(
        "Testing subjects:",
        sorted(groups_test.unique())
    )

    print(
        "Training repetitions:",
        len(X_train)
    )

    print(
        "Testing repetitions:",
        len(X_test)
    )


    # ========================================================
    # RANDOM FOREST
    # ========================================================

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        max_features="sqrt",
        n_jobs=-1
    )


    # Train
    model.fit(
        X_train,
        y_train
    )


    # Predict
    predictions = model.predict(
        X_test
    )


    # Accuracy
    accuracy = accuracy_score(
        y_test,
        predictions
    )

    fold_scores.append(
        accuracy
    )


    print(
        "Fold accuracy:",
        round(accuracy * 100, 2),
        "%"
    )


    # ========================================================
    # REPORT
    # ========================================================

    print("\nClassification report:")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "BAD FORM",
                "GOOD FORM"
            ],
            zero_division=0
        )
    )


    print("Confusion matrix:")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )


    fold_number += 1


# ============================================================
# CROSS VALIDATION SUMMARY
# ============================================================

average_accuracy = np.mean(
    fold_scores
)

standard_deviation = np.std(
    fold_scores
)


print("\n" + "=" * 60)
print("CROSS-VALIDATION SUMMARY")
print("=" * 60)

print(
    "\nFold accuracies:"
)

for i, score in enumerate(
    fold_scores,
    start=1
):

    print(
        f"Fold {i}: {score * 100:.2f}%"
    )


print(
    "\nAverage accuracy:",
    round(average_accuracy * 100, 2),
    "%"
)

print(
    "Standard deviation:",
    round(standard_deviation * 100, 2),
    "%"
)


# ============================================================
# TRAIN FINAL MODEL ON ALL DATA
# ============================================================

print("\n" + "=" * 60)
print("TRAINING FINAL MODEL ON ALL DATA")
print("=" * 60)


final_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    max_features="sqrt",
    n_jobs=-1
)


final_model.fit(
    X,
    y
)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    os.path.dirname(MODEL_FILE),
    exist_ok=True
)


import joblib

joblib.dump(
    {
        "model": final_model,
        "features": feature_columns
    },
    MODEL_FILE
)


print(
    "\nNormalized squat model saved successfully:"
)

print(
    MODEL_FILE
)


print("\n" + "=" * 60)
print("DONE")
print("=" * 60)