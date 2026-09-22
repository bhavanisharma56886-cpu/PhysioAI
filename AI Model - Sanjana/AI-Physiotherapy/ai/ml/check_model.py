import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "models" / "bicep_form_model.pkl"

package = joblib.load(MODEL_PATH)

model = package["model"]
feature_names = package["feature_names"]

print("\nMODEL LOADED SUCCESSFULLY")
print("--------------------------------")
print("Number of features:", len(feature_names))

print("\nFeatures expected by the model:")
for i, feature in enumerate(feature_names, start=1):
    print(f"{i}. {feature}")