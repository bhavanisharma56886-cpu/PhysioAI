# AI-Powered Physiotherapy Exercise Assistant

## AI / Machine Learning Module

This folder contains the AI and Computer Vision work for the Physiotherapy Exercise Assistant.

The current system supports:

- **Bicep Curl**
- **Squat**

Each exercise has a separate AI pipeline because the exercises require different body movements, features, datasets, and models.

---

## Bicep Curl

**Pipeline:**

Camera → YOLO Pose → Body Keypoints → Feature Extraction → Random Forest → GOOD/BAD FORM

The Bicep Curl system includes:

- YOLO pose detection
- Shoulder, elbow and wrist tracking
- Elbow-angle calculation
- ROM, repetition and speed analysis
- Machine-learning classification
- Live camera form prediction

**Model:**
`ml/models/bicep_form_model.pkl`

**Live program:**
`ml/live_bicep_form.py`

Run:

```bash
python ai/ml/live_bicep_form.py


Squat

Pipeline:

Camera → MediaPipe Pose → Body Landmarks → Feature Extraction → Random Forest → GOOD/BAD FORM

The Squat system includes:

Squat dataset verification
Body-landmark feature extraction
Knee and hip angle analysis
Distance, symmetry, velocity and depth features
Feature normalization
Random Forest classification
Live squat detection
Repetition counting
GOOD/BAD FORM prediction

Dataset:
data/raw/squat/rehab246_squat_positions_standardized.csv

Models:
ml/models/squat_form_model.pkl
ml/models/squat_form_model_normalized.pkl

Live program:
ml/squat/live_squat_form.py

Run:

python ai/ml/squat/live_squat_form.py
Technologies Used
Python
OpenCV
NumPy
Pandas
Scikit-learn
Random Forest
YOLO Pose
MediaPipe Pose



Project Structure
ai/
├── ml/
│   ├── models/
│   ├── squat/
│   ├── live_bicep_form.py
│   ├── train_model.py
│   └── evaluate_model.py
│
├── pose/
└── README.md