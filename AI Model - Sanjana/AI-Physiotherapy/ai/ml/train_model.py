import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

import joblib


# ============================================================
# 1. FILE PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GOOD_DATA = PROJECT_ROOT / "data" / "raw" / "features" / "batch_good_data.csv"
BAD_DATA = PROJECT_ROOT / "data" / "raw" / "features" / "batch_bad_data.csv"

MODEL_DIR = PROJECT_ROOT / "ai" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "bicep_form_model.pkl"


# ============================================================
# 2. LOAD PRESET DATA
# ============================================================

print("Loading preset dataset...")

good_df = pd.read_csv(GOOD_DATA)
bad_df = pd.read_csv(BAD_DATA)

print(f"Good-form samples: {len(good_df)}")
print(f"Bad-form samples:  {len(bad_df)}")


# ============================================================
# 3. COMBINE DATA
# ============================================================

df = pd.concat([good_df, bad_df], ignore_index=True)

print(f"\nTotal samples: {len(df)}")

print("\nLabel distribution:")
print(df["label"].value_counts())


# ============================================================
# 4. SEPARATE FEATURES AND LABEL
# ============================================================

X = df.drop(columns=["label"])
y = df["label"]


# ============================================================
# 5. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nDataset split:")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")


# ============================================================
# 6. CREATE RANDOM FOREST MODEL
# ============================================================

print("\nTraining Random Forest model...")

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# 7. TRAIN
# ============================================================

model.fit(X_train, y_train)

print("Training completed!")


# ============================================================
# 8. TEST MODEL
# ============================================================

print("\nTesting model...")

y_pred = model.predict(X_test)


# ============================================================
# 9. EVALUATION
# ============================================================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

cm = confusion_matrix(y_test, y_pred)


print("\n========================================")
print("MODEL RESULTS")
print("========================================")

print(f"Accuracy :  {accuracy:.4f}")
print(f"Precision:  {precision:.4f}")
print(f"Recall   :  {recall:.4f}")
print(f"F1 Score :  {f1:.4f}")

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["BAD FORM", "GOOD FORM"],
        zero_division=0
    )
)


# ============================================================
# 10. SAVE MODEL + FEATURE NAMES
# ============================================================

model_package = {
    "model": model,
    "feature_names": list(X.columns)
}

joblib.dump(model_package, MODEL_PATH)

print("\n========================================")
print("MODEL SAVED")
print("========================================")
print(f"Saved to: {MODEL_PATH}")