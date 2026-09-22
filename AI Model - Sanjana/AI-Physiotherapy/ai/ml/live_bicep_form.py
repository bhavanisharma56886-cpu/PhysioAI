import cv2
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from ultralytics import YOLO


# ============================================================
# 1. FIND PROJECT FOLDER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# 2. LOAD TRAINED ML MODEL
# ============================================================

MODEL_PATH = (
    PROJECT_ROOT
    / "ai"
    / "ml"
    / "models"
    / "bicep_form_model.pkl"
)

package = joblib.load(MODEL_PATH)

forest_model = package["model"]
feature_cols = package["feature_names"]

print("========================================")
print("✅ RANDOM FOREST MODEL LOADED")
print("========================================")
print("Number of features:", len(feature_cols))


# ============================================================
# 3. LOAD YOLO POSE MODEL
# ============================================================

YOLO_PATH = PROJECT_ROOT / "yolo11n-pose.pt"

yolo_model = YOLO(str(YOLO_PATH))

print("✅ YOLO POSE MODEL LOADED")
print("========================================")


# ============================================================
# 4. FUNCTION TO CALCULATE ANGLE
# ============================================================

def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = (
        np.arctan2(c[1] - b[1], c[0] - b[0])
        -
        np.arctan2(a[1] - b[1], a[0] - b[0])
    )

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


# ============================================================
# 5. VARIABLES FOR LIVE MOVEMENT
# ============================================================

prev_wrist_y = 0
prev_elbow_angle = 180

bad_form_cooldown = 0

current_message = "GOOD FORM"
current_color = (0, 255, 0)


# ============================================================
# 6. START CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("📷 CAMERA STARTED")
print("Perform a bicep curl.")
print("Press Q to stop.")
print("========================================")


# ============================================================
# 7. MAIN CAMERA LOOP
# ============================================================

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:

        print("❌ Could not read camera.")

        break


    # ========================================================
    # 8. YOLO POSE DETECTION
    # ========================================================

    results = yolo_model(
        frame,
        verbose=False
    )

    annotated_frame = results[0].plot()


    # ========================================================
    # 9. CHECK WHETHER PERSON WAS DETECTED
    # ========================================================

    if (
        results[0].keypoints is not None
        and len(results[0].keypoints.xyn) > 0
    ):

        # ----------------------------------------------------
        # Get bounding boxes
        # ----------------------------------------------------

        boxes = results[0].boxes.xyxy.cpu().numpy()


        # ----------------------------------------------------
        # Find largest person
        # ----------------------------------------------------

        areas = []

        for box in boxes:

            width = box[2] - box[0]
            height = box[3] - box[1]

            area = width * height

            areas.append(area)


        best_idx = int(np.argmax(areas))


        # ----------------------------------------------------
        # Get 17 normalized body keypoints
        # ----------------------------------------------------

        keypoints = (
            results[0]
            .keypoints
            .xyn[best_idx]
            .cpu()
            .numpy()
        )


        # ----------------------------------------------------
        # 17 keypoints × 2 = 34 values
        # ----------------------------------------------------

        flat_keypoints = keypoints.flatten()


        # ====================================================
        # 10. CALCULATE THE 7 ENGINEERED FEATURES
        # ====================================================

        # ----------------------------------------------------
        # Feature 1: Elbow Offset
        # ----------------------------------------------------

        elbow_offset = abs(
            keypoints[7][0]
            -
            keypoints[5][0]
        )


        # ----------------------------------------------------
        # Feature 2: Back Lean
        # ----------------------------------------------------

        vertical_ref = [
            keypoints[11][0],
            keypoints[11][1] - 0.5
        ]

        back_lean = calculate_angle(
            vertical_ref,
            keypoints[11],
            keypoints[5]
        )


        # ----------------------------------------------------
        # Feature 3: Wrist Velocity
        # ----------------------------------------------------

        current_wrist_y = keypoints[9][1]

        if prev_wrist_y == 0:

            wrist_velocity = 0

        else:

            wrist_velocity = (
                abs(
                    current_wrist_y
                    -
                    prev_wrist_y
                )
                * 100
            )

        prev_wrist_y = current_wrist_y


        # ----------------------------------------------------
        # Feature 4: Shoulder Shrug
        # ----------------------------------------------------

        shoulder_shrug = abs(
            keypoints[3][1]
            -
            keypoints[5][1]
        )


        # ----------------------------------------------------
        # Feature 5: Elbow Flare
        # ----------------------------------------------------

        elbow_flare = abs(
            keypoints[7][0]
            -
            keypoints[5][0]
        )


        # ----------------------------------------------------
        # Feature 6: Neck Angle
        # ----------------------------------------------------

        neck_angle = calculate_angle(
            keypoints[3],
            keypoints[5],
            keypoints[11]
        )


        # ----------------------------------------------------
        # Feature 7: Rep Phase
        # ----------------------------------------------------

        current_elbow_angle = calculate_angle(
            keypoints[5],
            keypoints[7],
            keypoints[9]
        )

        angle_change = (
            current_elbow_angle
            -
            prev_elbow_angle
        )

        if angle_change < -1:

            rep_phase = 1

        elif angle_change > 1:

            rep_phase = -1

        else:

            rep_phase = 0

        prev_elbow_angle = current_elbow_angle


        # ====================================================
        # 11. CREATE ALL 41 FEATURES
        # ====================================================

        input_values = [

            elbow_offset,
            back_lean,
            wrist_velocity,
            shoulder_shrug,
            elbow_flare,
            neck_angle,
            rep_phase

        ] + flat_keypoints.tolist()


        # ====================================================
        # 12. CREATE DATAFRAME
        # ====================================================

        input_df = pd.DataFrame(
            [input_values],
            columns=feature_cols
        )


        # ====================================================
        # 13. MODEL PREDICTION
        # ====================================================

        prediction = forest_model.predict(
            input_df
        )[0]

        probability = (
            forest_model
            .predict_proba(input_df)[0][prediction]
        )


        # ====================================================
        # 14. GOOD FORM / BAD FORM
        # ====================================================

        if prediction == 0:

            bad_form_cooldown = 30

            current_message = (
                f"BAD FORM ({probability * 100:.0f}%)"
            )

            current_color = (0, 0, 255)


        elif bad_form_cooldown > 0:

            bad_form_cooldown -= 1


        else:

            current_message = (
                f"GOOD FORM ({probability * 100:.0f}%)"
            )

            current_color = (0, 255, 0)


        # ====================================================
        # 15. DRAW BOX AROUND PERSON
        # ====================================================

        box = boxes[best_idx].astype(int)

        cv2.rectangle(
            annotated_frame,
            (box[0], box[1]),
            (box[2], box[3]),
            current_color,
            4
        )


        # ====================================================
        # 16. DRAW FORM MESSAGE
        # ====================================================

        label_top = max(0, box[1] - 45)

        cv2.rectangle(
            annotated_frame,
            (box[0], label_top),
            (box[0] + 350, box[1]),
            current_color,
            -1
        )

        cv2.putText(
            annotated_frame,
            current_message,
            (box[0] + 5, box[1] - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        # ====================================================
        # 17. DISPLAY ELBOW ANGLE
        # ====================================================

        cv2.putText(
            annotated_frame,
            f"Elbow Angle: {current_elbow_angle:.1f}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


    # ========================================================
    # 18. SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "AI Physiotherapy - Bicep Curl",
        annotated_frame
    )


    # ========================================================
    # 19. PRESS Q TO EXIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# 20. CLOSE CAMERA
# ============================================================

cap.release()

cv2.destroyAllWindows()

print("👋 Camera stopped.")