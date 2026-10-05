import cv2
import math
import time
import joblib
import numpy as np
import pandas as pd
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = r"C:\Users\hp\Desktop\AI-Physiotherapy\ai\ml\models\squat_form_model_normalized.pkl"
POSE_MODEL_PATH = r"C:\Users\hp\Desktop\AI-Physiotherapy\ai\ml\squat\pose_landmarker_lite.task"


# ============================================================
# SETTINGS
# ============================================================

CAMERA_INDEX = 0

MIN_DETECTION_CONFIDENCE = 0.5
MIN_PRESENCE_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# ------------------------------------------------------------
# SQUAT REP DETECTION
# ------------------------------------------------------------

# Person must bend below this angle to START a squat.
START_KNEE_ANGLE = 150

# Person must reach this deeper angle before we consider
# the squat to have actually reached the bottom.
DEPTH_KNEE_ANGLE = 130

# Person must return above this angle to finish the squat.
END_KNEE_ANGLE = 160

# Number of consecutive standing frames required.
END_HOLD_FRAMES = 5

# Minimum frames in a valid repetition.
MIN_REP_FRAMES = 25

# Minimum number of frames that must show meaningful
# squat depth before the rep can be counted.
MIN_DEPTH_FRAMES = 5

# Prevent immediate accidental re-triggering.
COOLDOWN_FRAMES = 15


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

print("Loading squat model...")

bundle = joblib.load(MODEL_PATH)

if isinstance(bundle, dict):

    model = bundle.get("model")

    if model is None:
        model = bundle.get("classifier")

    feature_names = bundle.get("features")

    if feature_names is None:
        feature_names = bundle.get("feature_names")

else:

    model = bundle
    feature_names = None


if model is None:
    raise RuntimeError(
        "Could not find the trained Random Forest model."
    )


if feature_names is None:
    raise RuntimeError(
        "The squat model does not contain its feature list."
    )


print("Squat model loaded successfully.")
print("Expected ML features:", len(feature_names))


# ============================================================
# MEDIAPIPE POSE LANDMARKER
# ============================================================

print("Loading MediaPipe Pose Landmarker...")

base_options = python.BaseOptions(
    model_asset_path=POSE_MODEL_PATH
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=MIN_DETECTION_CONFIDENCE,
    min_pose_presence_confidence=MIN_PRESENCE_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE
)

landmarker = vision.PoseLandmarker.create_from_options(
    options
)

print("MediaPipe Pose Landmarker loaded successfully.")


# ============================================================
# CONSTANTS
# ============================================================

STAT_NAMES = [
    "mean",
    "std",
    "min",
    "max",
    "range",
    "q10",
    "q25",
    "median",
    "q75",
    "q90"
]


# ============================================================
# MATH FUNCTIONS
# ============================================================

def angle_2d(a, b, c):

    """
    Calculates angle ABC in degrees.
    """

    ba = np.array(
        [
            a[0] - b[0],
            a[1] - b[1]
        ],
        dtype=float
    )

    bc = np.array(
        [
            c[0] - b[0],
            c[1] - b[1]
        ],
        dtype=float
    )

    denominator = (
        np.linalg.norm(ba)
        *
        np.linalg.norm(bc)
    )

    if denominator < 1e-8:
        return 0.0

    cosine = np.dot(ba, bc) / denominator

    cosine = np.clip(
        cosine,
        -1.0,
        1.0
    )

    return float(
        np.degrees(
            np.arccos(cosine)
        )
    )


def distance_2d(a, b):

    return float(
        math.sqrt(
            (a[0] - b[0]) ** 2 +
            (a[1] - b[1]) ** 2
        )
    )


def safe_divide(a, b):

    if abs(b) > 1e-8:
        return float(a / b)

    return 0.0


# ============================================================
# STATISTICAL SUMMARY
# ============================================================

def summarize(values, prefix):

    values = np.asarray(
        values,
        dtype=float
    )

    return {

        f"{prefix}_mean":
            float(np.mean(values)),

        f"{prefix}_std":
            float(np.std(values)),

        f"{prefix}_min":
            float(np.min(values)),

        f"{prefix}_max":
            float(np.max(values)),

        f"{prefix}_range":
            float(
                np.max(values) -
                np.min(values)
            ),

        f"{prefix}_q10":
            float(np.percentile(values, 10)),

        f"{prefix}_q25":
            float(np.percentile(values, 25)),

        f"{prefix}_median":
            float(np.percentile(values, 50)),

        f"{prefix}_q75":
            float(np.percentile(values, 75)),

        f"{prefix}_q90":
            float(np.percentile(values, 90))
    }


# ============================================================
# GET MEDIAPIPE BODY POINTS
# ============================================================

def get_points(landmarks):

    return {

        "left_shoulder": (
            landmarks[11].x,
            landmarks[11].y
        ),

        "right_shoulder": (
            landmarks[12].x,
            landmarks[12].y
        ),

        "left_hip": (
            landmarks[23].x,
            landmarks[23].y
        ),

        "right_hip": (
            landmarks[24].x,
            landmarks[24].y
        ),

        "left_knee": (
            landmarks[25].x,
            landmarks[25].y
        ),

        "right_knee": (
            landmarks[26].x,
            landmarks[26].y
        ),

        "left_ankle": (
            landmarks[27].x,
            landmarks[27].y
        ),

        "right_ankle": (
            landmarks[28].x,
            landmarks[28].y
        )
    }


# ============================================================
# CALCULATE EXACT FRAME FEATURES
# ============================================================

def calculate_frame_features(p):

    # --------------------------------------------------------
    # KNEE ANGLES
    # --------------------------------------------------------

    left_knee_angle = angle_2d(
        p["left_hip"],
        p["left_knee"],
        p["left_ankle"]
    )

    right_knee_angle = angle_2d(
        p["right_hip"],
        p["right_knee"],
        p["right_ankle"]
    )

    # --------------------------------------------------------
    # HIP ANGLES
    # --------------------------------------------------------

    left_hip_angle = angle_2d(
        p["left_shoulder"],
        p["left_hip"],
        p["left_knee"]
    )

    right_hip_angle = angle_2d(
        p["right_shoulder"],
        p["right_hip"],
        p["right_knee"]
    )

    # --------------------------------------------------------
    # MIDPOINTS
    # --------------------------------------------------------

    shoulder_mid = (

        (
            p["left_shoulder"][0] +
            p["right_shoulder"][0]
        ) / 2,

        (
            p["left_shoulder"][1] +
            p["right_shoulder"][1]
        ) / 2
    )

    hip_mid = (

        (
            p["left_hip"][0] +
            p["right_hip"][0]
        ) / 2,

        (
            p["left_hip"][1] +
            p["right_hip"][1]
        ) / 2
    )

    # --------------------------------------------------------
    # TORSO ANGLE
    # --------------------------------------------------------

    dx = (
        shoulder_mid[0] -
        hip_mid[0]
    )

    dy = (
        shoulder_mid[1] -
        hip_mid[1]
    )

    torso_angle = abs(
        np.degrees(
            np.arctan2(
                dx,
                -dy
            )
        )
    )

    # --------------------------------------------------------
    # DISTANCES
    # --------------------------------------------------------

    knee_distance = distance_2d(
        p["left_knee"],
        p["right_knee"]
    )

    hip_distance = distance_2d(
        p["left_hip"],
        p["right_hip"]
    )

    ankle_distance = distance_2d(
        p["left_ankle"],
        p["right_ankle"]
    )

    body_scale = max(
        hip_distance,
        0.0001
    )

    # --------------------------------------------------------
    # KNEE / ANKLE HORIZONTAL POSITION
    # --------------------------------------------------------

    left_knee_ankle_horizontal = (
        abs(
            p["left_knee"][0] -
            p["left_ankle"][0]
        )
        / body_scale
    )

    right_knee_ankle_horizontal = (
        abs(
            p["right_knee"][0] -
            p["right_ankle"][0]
        )
        / body_scale
    )

    # --------------------------------------------------------
    # VERTICAL FEATURES
    # --------------------------------------------------------

    hip_vertical = hip_mid[1]

    left_knee_vertical = (
        p["left_knee"][1]
    )

    right_knee_vertical = (
        p["right_knee"][1]
    )

    torso_vertical = abs(
        shoulder_mid[1] -
        hip_mid[1]
    )

    # --------------------------------------------------------
    # SYMMETRY
    # --------------------------------------------------------

    knee_angle_difference = abs(
        left_knee_angle -
        right_knee_angle
    )

    hip_angle_difference = abs(
        left_hip_angle -
        right_hip_angle
    )

    return {

        "left_knee_angle":
            left_knee_angle,

        "right_knee_angle":
            right_knee_angle,

        "left_hip_angle":
            left_hip_angle,

        "right_hip_angle":
            right_hip_angle,

        "torso_angle":
            torso_angle,

        "knee_distance":
            knee_distance,

        "hip_distance":
            hip_distance,

        "ankle_distance":
            ankle_distance,

        "left_knee_ankle_horizontal":
            left_knee_ankle_horizontal,

        "right_knee_ankle_horizontal":
            right_knee_ankle_horizontal,

        "hip_vertical":
            hip_vertical,

        "left_knee_vertical":
            left_knee_vertical,

        "right_knee_vertical":
            right_knee_vertical,

        "torso_vertical":
            torso_vertical,

        "knee_angle_difference":
            knee_angle_difference,

        "hip_angle_difference":
            hip_angle_difference
    }


# ============================================================
# BUILD EXACT REPETITION FEATURES
# ============================================================

def build_rep_features(frames):

    if len(frames) < MIN_REP_FRAMES:
        return None

    feature_dict = {}

    # --------------------------------------------------------
    # SEQUENCES
    # --------------------------------------------------------

    sequence_names = [

        "left_knee_angle",
        "right_knee_angle",
        "left_hip_angle",
        "right_hip_angle",
        "torso_angle",
        "knee_angle_difference",
        "hip_angle_difference",
        "knee_distance",
        "hip_distance",
        "ankle_distance",
        "left_knee_ankle_horizontal",
        "right_knee_ankle_horizontal",
        "hip_vertical",
        "left_knee_vertical",
        "right_knee_vertical",
        "torso_vertical"
    ]

    sequences = {}

    for name in sequence_names:

        sequences[name] = np.array(
            [
                frame[name]
                for frame in frames
            ],
            dtype=float
        )

    # --------------------------------------------------------
    # ANGLES
    # --------------------------------------------------------

    angle_names = [

        "left_knee_angle",
        "right_knee_angle",
        "left_hip_angle",
        "right_hip_angle",
        "torso_angle",
        "knee_angle_difference",
        "hip_angle_difference"
    ]

    for name in angle_names:

        feature_dict.update(
            summarize(
                sequences[name],
                name
            )
        )

    # --------------------------------------------------------
    # DISTANCES
    # --------------------------------------------------------

    distance_names = [

        "knee_distance",
        "hip_distance",
        "ankle_distance"
    ]

    for name in distance_names:

        feature_dict.update(
            summarize(
                sequences[name],
                name
            )
        )

    # --------------------------------------------------------
    # HORIZONTAL FEATURES
    # --------------------------------------------------------

    horizontal_names = [

        "left_knee_ankle_horizontal",
        "right_knee_ankle_horizontal"
    ]

    for name in horizontal_names:

        feature_dict.update(
            summarize(
                sequences[name],
                name
            )
        )

    # --------------------------------------------------------
    # VERTICAL FEATURES
    # --------------------------------------------------------

    vertical_names = [

        "hip_vertical",
        "left_knee_vertical",
        "right_knee_vertical",
        "torso_vertical"
    ]

    for name in vertical_names:

        feature_dict.update(
            summarize(
                sequences[name],
                name
            )
        )

    # --------------------------------------------------------
    # VELOCITY
    # --------------------------------------------------------

    velocity_source_names = [

        "left_knee_angle",
        "right_knee_angle",
        "left_hip_angle",
        "right_hip_angle",
        "torso_angle"
    ]

    velocity_output_names = [

        "left_knee_velocity",
        "right_knee_velocity",
        "left_hip_velocity",
        "right_hip_velocity",
        "torso_velocity"
    ]

    for source, output in zip(
        velocity_source_names,
        velocity_output_names
    ):

        values = np.abs(
            np.diff(
                sequences[source]
            )
        )

        if len(values) == 0:
            values = np.array([0.0])

        feature_dict.update(
            summarize(
                values,
                output
            )
        )

    # --------------------------------------------------------
    # DEPTH FEATURES
    # --------------------------------------------------------

    feature_dict[
        "left_knee_flexion_depth"
    ] = (
        180.0 -
        np.min(
            sequences["left_knee_angle"]
        )
    )

    feature_dict[
        "right_knee_flexion_depth"
    ] = (
        180.0 -
        np.min(
            sequences["right_knee_angle"]
        )
    )

    feature_dict[
        "left_hip_flexion_depth"
    ] = (
        180.0 -
        np.min(
            sequences["left_hip_angle"]
        )
    )

    feature_dict[
        "right_hip_flexion_depth"
    ] = (
        180.0 -
        np.min(
            sequences["right_hip_angle"]
        )
    )

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    hip_distance_mean = feature_dict[
        "hip_distance_mean"
    ]

    distance_bases = [

        "knee_distance",
        "hip_distance",
        "ankle_distance"
    ]

    distance_stats = [

        "mean",
        "std",
        "min",
        "max",
        "range"
    ]

    for base in distance_bases:

        for stat in distance_stats:

            if (
                base == "hip_distance"
                and stat == "mean"
            ):
                continue

            source_name = (
                f"{base}_{stat}"
            )

            normalized_name = (
                f"{base}_{stat}_normalized"
            )

            feature_dict[
                normalized_name
            ] = safe_divide(
                feature_dict[source_name],
                hip_distance_mean
            )

    # --------------------------------------------------------
    # HORIZONTAL NORMALIZATION
    # --------------------------------------------------------

    for base in horizontal_names:

        for stat in STAT_NAMES:

            source_name = (
                f"{base}_{stat}"
            )

            normalized_name = (
                f"{base}_{stat}_normalized"
            )

            feature_dict[
                normalized_name
            ] = safe_divide(
                feature_dict[source_name],
                hip_distance_mean
            )

    # --------------------------------------------------------
    # VERTICAL NORMALIZATION
    # --------------------------------------------------------

    for base in vertical_names:

        for stat in STAT_NAMES:

            source_name = (
                f"{base}_{stat}"
            )

            normalized_name = (
                f"{base}_{stat}_normalized"
            )

            feature_dict[
                normalized_name
            ] = safe_divide(
                feature_dict[source_name],
                hip_distance_mean
            )

    return feature_dict


# ============================================================
# PREPARE MODEL INPUT
# ============================================================

def prepare_model_input(feature_dict):

    missing_features = [

        name

        for name in feature_names

        if name not in feature_dict
    ]

    if missing_features:

        print("\nERROR: Missing model features:")

        for name in missing_features:
            print("   ", name)

        return None

    values = [

        feature_dict[name]

        for name in feature_names
    ]

    X = pd.DataFrame(
        [values],
        columns=feature_names
    )

    return X


# ============================================================
# PREDICT ONE REPETITION
# ============================================================

def predict_repetition(frames):

    print(
        f"\nAnalyzing repetition with "
        f"{len(frames)} frames..."
    )

    feature_dict = build_rep_features(
        frames
    )

    if feature_dict is None:

        print(
            "Repetition too short. Ignored."
        )

        return None, 0.0

    X = prepare_model_input(
        feature_dict
    )

    if X is None:
        return None, 0.0

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    confidence = float(
        np.max(probabilities)
    )

    if int(prediction) == 1:
        result = "GOOD FORM"
    else:
        result = "BAD FORM"

    print(
        f"Prediction: {result}"
    )

    print(
        f"Confidence: {confidence * 100:.2f}%"
    )

    return result, confidence


# ============================================================
# CAMERA
# ============================================================

print("\nOpening camera...")

cap = cv2.VideoCapture(
    CAMERA_INDEX
)

if not cap.isOpened():

    raise RuntimeError(
        "Could not open camera."
    )

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)


print()
print("================================================")
print("      AI PHYSIOTHERAPY - SQUAT DETECTION")
print("================================================")
print()
print("Camera is ready.")
print()
print("Stand normally first.")
print("Then perform one complete squat.")
print()
print("The program will automatically:")
print("1. Detect the squat")
print("2. Check squat depth")
print("3. Collect the repetition")
print("4. Analyze the repetition")
print("5. Predict GOOD FORM / BAD FORM")
print()
print("Press Q to quit.")
print("================================================")
print()


# ============================================================
# STATE VARIABLES
# ============================================================

frame_number = 0

rep_frames = []

state = "WAITING"

standing_frames = 0

depth_frames = 0

rep_count = 0

last_prediction = "WAITING"

last_confidence = 0.0

missing_pose_frames = 0

cooldown_remaining = 0


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        success, frame = cap.read()

        if not success:

            print(
                "Could not read camera frame."
            )

            break

        frame_number += 1

        # ----------------------------------------------------
        # MIRROR CAMERA
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )

        # ----------------------------------------------------
        # BGR -> RGB
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp_ms = int(
            time.monotonic() * 1000
        )

        # ----------------------------------------------------
        # MEDIAPIPE
        # ----------------------------------------------------

        result = landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        # ----------------------------------------------------
        # COOLDOWN
        # ----------------------------------------------------

        if cooldown_remaining > 0:

            cooldown_remaining -= 1

        # ----------------------------------------------------
        # POSE FOUND
        # ----------------------------------------------------

        if result.pose_landmarks:

            missing_pose_frames = 0

            landmarks = (
                result.pose_landmarks[0]
            )

            points = get_points(
                landmarks
            )

            frame_features = (
                calculate_frame_features(
                    points
                )
            )

            # ------------------------------------------------
            # AVERAGE KNEE ANGLE
            # ------------------------------------------------

            average_knee_angle = (

                frame_features[
                    "left_knee_angle"
                ]

                +

                frame_features[
                    "right_knee_angle"
                ]

            ) / 2.0

            # ------------------------------------------------
            # DRAW LANDMARKS
            # ------------------------------------------------

            h, w, _ = frame.shape

            for landmark in landmarks:

                x = int(
                    landmark.x * w
                )

                y = int(
                    landmark.y * h
                )

                if (
                    0 <= x < w
                    and
                    0 <= y < h
                ):

                    cv2.circle(
                        frame,
                        (x, y),
                        4,
                        (255, 255, 255),
                        -1
                    )

            # =================================================
            # WAITING
            # =================================================

            if state == "WAITING":

                standing_frames = 0
                depth_frames = 0

                # ------------------------------------------------
                # Only allow a new rep after cooldown.
                # ------------------------------------------------

                if cooldown_remaining == 0:

                    if (
                        average_knee_angle
                        < START_KNEE_ANGLE
                    ):

                        state = "COLLECTING"

                        rep_frames = []

                        standing_frames = 0

                        depth_frames = 0

                        rep_frames.append(
                            frame_features
                        )

            # =================================================
            # COLLECTING
            # =================================================

            elif state == "COLLECTING":

                rep_frames.append(
                    frame_features
                )

                # ------------------------------------------------
                # CHECK WHETHER REAL SQUAT DEPTH WAS REACHED
                # ------------------------------------------------

                if (
                    average_knee_angle
                    <= DEPTH_KNEE_ANGLE
                ):

                    depth_frames += 1

                # ------------------------------------------------
                # RETURN TO STANDING
                # ------------------------------------------------

                if (
                    average_knee_angle
                    >= END_KNEE_ANGLE
                ):

                    standing_frames += 1

                else:

                    standing_frames = 0

                # ------------------------------------------------
                # REP FINISHED
                # ------------------------------------------------

                if (
                    standing_frames
                    >= END_HOLD_FRAMES
                ):

                    # --------------------------------------------
                    # FIRST CHECK:
                    # Did the person actually reach squat depth?
                    # --------------------------------------------

                    if depth_frames < MIN_DEPTH_FRAMES:

                        print(
                            "\nMovement detected "
                            "but squat depth was insufficient."
                        )

                        print(
                            "Movement ignored."
                        )

                    # --------------------------------------------
                    # SECOND CHECK:
                    # Was the movement long enough?
                    # --------------------------------------------

                    elif len(rep_frames) < MIN_REP_FRAMES:

                        print(
                            "\nRep too short. Ignored."
                        )

                    # --------------------------------------------
                    # VALID REP
                    # --------------------------------------------

                    else:

                        result_text, confidence = (
                            predict_repetition(
                                rep_frames
                            )
                        )

                        if result_text is not None:

                            rep_count += 1

                            last_prediction = (
                                result_text
                            )

                            last_confidence = (
                                confidence
                            )

                            print(
                                f"REP {rep_count} COMPLETE"
                            )

                    # --------------------------------------------
                    # RESET
                    # --------------------------------------------

                    rep_frames = []

                    standing_frames = 0

                    depth_frames = 0

                    state = "WAITING"

                    cooldown_remaining = (
                        COOLDOWN_FRAMES
                    )

        # =====================================================
        # NO POSE
        # =====================================================

        else:

            missing_pose_frames += 1

            cv2.putText(
                frame,
                "NO PERSON DETECTED",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2
            )

            # ------------------------------------------------
            # Reset incomplete squat if person disappears.
            # ------------------------------------------------

            if (
                missing_pose_frames > 20
                and
                state == "COLLECTING"
            ):

                rep_frames = []

                standing_frames = 0

                depth_frames = 0

                state = "WAITING"

        # =====================================================
        # DISPLAY PANEL
        # =====================================================

        cv2.rectangle(
            frame,
            (20, 70),
            (500, 270),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            frame,
            f"STATE: {state}",
            (35, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"REPS: {rep_count}",
            (35, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"RESULT: {last_prediction}",
            (35, 175),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"CONFIDENCE: {last_confidence * 100:.1f}%",
            (35, 210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"DEPTH FRAMES: {depth_frames}",
            (35, 245),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        # =====================================================
        # INSTRUCTIONS
        # =====================================================

        if state == "WAITING":

            cv2.putText(
                frame,
                "Ready - perform a full squat",
                (30, 310),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        elif state == "COLLECTING":

            cv2.putText(
                frame,
                "Squat detected - continue movement",
                (30, 310),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        # =====================================================
        # SHOW CAMERA
        # =====================================================

        cv2.imshow(
            "AI Physiotherapy - Squat Form",
            frame
        )

        # =====================================================
        # QUIT
        # =====================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break


finally:

    cap.release()

    cv2.destroyAllWindows()

    landmarker.close()

    print()
    print("Camera closed.")
    print("Squat live detection stopped.")