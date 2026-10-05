import os
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import accuracy_score


# ---------------------------------------------------------
# FILE PATH
# ---------------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

FEATURE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "features",
    "squat_features.csv"
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("=" * 60)
print("SQUAT SUBJECT-BASED CROSS VALIDATION")
print("=" * 60)

print()
print("Loading feature dataset...")

df = pd.read_csv(FEATURE_FILE)

print("Dataset shape:", df.shape)


# ---------------------------------------------------------
# PREPARE FEATURES
# ---------------------------------------------------------

X = df.drop(
    columns=[
        "is_correct",
        "subject_id",
        "repetition"
    ]
)

y = df["is_correct"].astype(int)

groups = df["subject_id"]


print()
print("Number of ML features:", X.shape[1])

print(
    "Good repetitions:",
    int(y.sum())
)

print(
    "Bad repetitions:",
    int((y == 0).sum())
)

print(
    "Number of subjects:",
    groups.nunique()
)


# ---------------------------------------------------------
# CROSS VALIDATION
# ---------------------------------------------------------

print()
print("Running subject-based cross validation...")
print()

group_kfold = GroupKFold(
    n_splits=3
)

accuracies = []

fold_number = 1


for train_index, test_index in group_kfold.split(
    X,
    y,
    groups
):

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = y.iloc[train_index]
    y_test = y.iloc[test_index]

    train_subjects = sorted(
        groups.iloc[train_index].unique()
    )

    test_subjects = sorted(
        groups.iloc[test_index].unique()
    )


    print("-" * 60)
    print("FOLD", fold_number)
    print("-" * 60)

    print(
        "Training subjects:",
        train_subjects
    )

    print(
        "Testing subjects:",
        test_subjects
    )

    print(
        "Training repetitions:",
        len(X_train)
    )

    print(
        "Testing repetitions:",
        len(X_test)
    )


    # -----------------------------------------------------
    # TRAIN MODEL
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # TEST MODEL
    # -----------------------------------------------------

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    accuracies.append(accuracy)

    print(
        "Fold accuracy:",
        round(accuracy * 100, 2),
        "%"
    )

    fold_number += 1


# ---------------------------------------------------------
# FINAL RESULT
# ---------------------------------------------------------

print()
print("=" * 60)
print("CROSS-VALIDATION RESULTS")
print("=" * 60)

for i, accuracy in enumerate(
    accuracies,
    start=1
):

    print(
        f"Fold {i}: {accuracy * 100:.2f}%"
    )


mean_accuracy = np.mean(
    accuracies
)

std_accuracy = np.std(
    accuracies
)


print()
print(
    "Average accuracy:",
    f"{mean_accuracy * 100:.2f}%"
)

print(
    "Standard deviation:",
    f"{std_accuracy * 100:.2f}%"
)

print()
print("=" * 60)
print("CROSS-VALIDATION COMPLETE")
print("=" * 60)