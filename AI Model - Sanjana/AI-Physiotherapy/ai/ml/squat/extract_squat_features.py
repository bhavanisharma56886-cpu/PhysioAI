import os
import numpy as np
import pandas as pd


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "squat",
    "rehab246_squat_positions_standardized.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "features",
    "squat_features.csv"
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def angle_2d(a, b, c):
    """Calculate angle ABC using 2D X/Y coordinates."""

    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)

    if denominator == 0:
        return np.nan

    cosine_angle = np.dot(ba, bc) / denominator
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    return np.degrees(np.arccos(cosine_angle))


def distance_2d(a, b):
    """Calculate 2D distance between two points."""

    return np.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2
    )


def summarize(values, prefix):
    """Create statistical features from a movement sequence."""

    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return {}

    return {
        f"{prefix}_mean": np.mean(values),
        f"{prefix}_std": np.std(values),
        f"{prefix}_min": np.min(values),
        f"{prefix}_max": np.max(values),
        f"{prefix}_range": np.max(values) - np.min(values),
        f"{prefix}_q10": np.percentile(values, 10),
        f"{prefix}_q25": np.percentile(values, 25),
        f"{prefix}_median": np.percentile(values, 50),
        f"{prefix}_q75": np.percentile(values, 75),
        f"{prefix}_q90": np.percentile(values, 90),
    }


# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------

print("Loading squat dataset...")

df = pd.read_csv(INPUT_FILE)

print("Total frames:", len(df))


# ---------------------------------------------------------
# PROCESS EACH REPETITION
# ---------------------------------------------------------

all_features = []

groups = df.groupby(["subject_id", "repetition"])

print("Total repetitions:", len(groups))


for (subject_id, repetition), group in groups:

    group = group.sort_values("frame").reset_index(drop=True)

    left_knee_angles = []
    right_knee_angles = []

    left_hip_angles = []
    right_hip_angles = []

    torso_angles = []

    knee_distances = []
    hip_distances = []
    ankle_distances = []

    normalized_knee_distances = []

    left_knee_ankle_horizontal = []
    right_knee_ankle_horizontal = []

    hip_vertical = []

    left_knee_vertical = []
    right_knee_vertical = []

    knee_angle_difference = []
    hip_angle_difference = []

    torso_vertical = []


    # -----------------------------------------------------
    # FRAME-BY-FRAME FEATURES
    # -----------------------------------------------------

    for _, row in group.iterrows():

        # LEFT SIDE

        ls = (
            row["LeftShoulder_X"],
            row["LeftShoulder_Y"]
        )

        le = (
            row["LeftElbow_X"],
            row["LeftElbow_Y"]
        )

        lw = (
            row["LeftWrist_X"],
            row["LeftWrist_Y"]
        )

        lh = (
            row["LeftHip_X"],
            row["LeftHip_Y"]
        )

        lk = (
            row["LeftKnee_X"],
            row["LeftKnee_Y"]
        )

        la = (
            row["LeftAnkle_X"],
            row["LeftAnkle_Y"]
        )


        # RIGHT SIDE

        rs = (
            row["RightShoulder_X"],
            row["RightShoulder_Y"]
        )

        re = (
            row["RightElbow_X"],
            row["RightElbow_Y"]
        )

        rw = (
            row["RightWrist_X"],
            row["RightWrist_Y"]
        )

        rh = (
            row["RightHip_X"],
            row["RightHip_Y"]
        )

        rk = (
            row["RightKnee_X"],
            row["RightKnee_Y"]
        )

        ra = (
            row["RightAnkle_X"],
            row["RightAnkle_Y"]
        )


        # -------------------------------------------------
        # KNEE ANGLES
        # -------------------------------------------------

        left_knee_angle = angle_2d(
            lh,
            lk,
            la
        )

        right_knee_angle = angle_2d(
            rh,
            rk,
            ra
        )

        left_knee_angles.append(left_knee_angle)
        right_knee_angles.append(right_knee_angle)


        # -------------------------------------------------
        # HIP ANGLES
        # -------------------------------------------------

        left_hip_angle = angle_2d(
            ls,
            lh,
            lk
        )

        right_hip_angle = angle_2d(
            rs,
            rh,
            rk
        )

        left_hip_angles.append(left_hip_angle)
        right_hip_angles.append(right_hip_angle)


        # -------------------------------------------------
        # TORSO ANGLE
        # -------------------------------------------------

        shoulder_mid = (
            (ls[0] + rs[0]) / 2,
            (ls[1] + rs[1]) / 2
        )

        hip_mid = (
            (lh[0] + rh[0]) / 2,
            (lh[1] + rh[1]) / 2
        )

        dx = shoulder_mid[0] - hip_mid[0]
        dy = shoulder_mid[1] - hip_mid[1]

        torso_angle = abs(
            np.degrees(
                np.arctan2(dx, -dy)
            )
        )

        torso_angles.append(torso_angle)


        # -------------------------------------------------
        # DISTANCES
        # -------------------------------------------------

        knee_distance = distance_2d(
            lk,
            rk
        )

        hip_distance = distance_2d(
            lh,
            rh
        )

        ankle_distance = distance_2d(
            la,
            ra
        )

        knee_distances.append(knee_distance)
        hip_distances.append(hip_distance)
        ankle_distances.append(ankle_distance)


        # -------------------------------------------------
        # NORMALIZED KNEE DISTANCE
        # -------------------------------------------------

        body_scale = max(
            hip_distance,
            0.0001
        )

        normalized_knee_distances.append(
            knee_distance / body_scale
        )


        # -------------------------------------------------
        # KNEE VS ANKLE POSITION
        # -------------------------------------------------

        left_knee_ankle_horizontal.append(
            abs(lk[0] - la[0]) / body_scale
        )

        right_knee_ankle_horizontal.append(
            abs(rk[0] - ra[0]) / body_scale
        )


        # -------------------------------------------------
        # VERTICAL POSITIONS
        # -------------------------------------------------

        hip_vertical.append(
            (lh[1] + rh[1]) / 2
        )

        left_knee_vertical.append(
            lk[1]
        )

        right_knee_vertical.append(
            rk[1]
        )

        torso_vertical.append(
            abs(
                shoulder_mid[1] -
                hip_mid[1]
            )
        )


        # -------------------------------------------------
        # LEFT / RIGHT SYMMETRY
        # -------------------------------------------------

        knee_angle_difference.append(
            abs(
                left_knee_angle -
                right_knee_angle
            )
        )

        hip_angle_difference.append(
            abs(
                left_hip_angle -
                right_hip_angle
            )
        )


    # -----------------------------------------------------
    # VELOCITY
    # -----------------------------------------------------

    def velocity(values):

        values = np.asarray(
            values,
            dtype=float
        )

        if len(values) < 2:
            return np.array([0.0])

        return np.abs(
            np.diff(values)
        )


    left_knee_velocity = velocity(
        left_knee_angles
    )

    right_knee_velocity = velocity(
        right_knee_angles
    )

    left_hip_velocity = velocity(
        left_hip_angles
    )

    right_hip_velocity = velocity(
        right_hip_angles
    )

    torso_velocity = velocity(
        torso_angles
    )


    # -----------------------------------------------------
    # CREATE FEATURE ROW
    # -----------------------------------------------------

    features = {}


    # ANGLE FEATURES

    features.update(
        summarize(
            left_knee_angles,
            "left_knee_angle"
        )
    )

    features.update(
        summarize(
            right_knee_angles,
            "right_knee_angle"
        )
    )

    features.update(
        summarize(
            left_hip_angles,
            "left_hip_angle"
        )
    )

    features.update(
        summarize(
            right_hip_angles,
            "right_hip_angle"
        )
    )

    features.update(
        summarize(
            torso_angles,
            "torso_angle"
        )
    )


    # DISTANCE FEATURES

    features.update(
        summarize(
            knee_distances,
            "knee_distance"
        )
    )

    features.update(
        summarize(
            hip_distances,
            "hip_distance"
        )
    )

    features.update(
        summarize(
            ankle_distances,
            "ankle_distance"
        )
    )

    features.update(
        summarize(
            normalized_knee_distances,
            "normalized_knee_distance"
        )
    )


    # KNEE / ANKLE RELATIONSHIP

    features.update(
        summarize(
            left_knee_ankle_horizontal,
            "left_knee_ankle_horizontal"
        )
    )

    features.update(
        summarize(
            right_knee_ankle_horizontal,
            "right_knee_ankle_horizontal"
        )
    )


    # VERTICAL MOVEMENT

    features.update(
        summarize(
            hip_vertical,
            "hip_vertical"
        )
    )

    features.update(
        summarize(
            left_knee_vertical,
            "left_knee_vertical"
        )
    )

    features.update(
        summarize(
            right_knee_vertical,
            "right_knee_vertical"
        )
    )

    features.update(
        summarize(
            torso_vertical,
            "torso_vertical"
        )
    )


    # SYMMETRY FEATURES

    features.update(
        summarize(
            knee_angle_difference,
            "knee_angle_difference"
        )
    )

    features.update(
        summarize(
            hip_angle_difference,
            "hip_angle_difference"
        )
    )


    # VELOCITY FEATURES

    features.update(
        summarize(
            left_knee_velocity,
            "left_knee_velocity"
        )
    )

    features.update(
        summarize(
            right_knee_velocity,
            "right_knee_velocity"
        )
    )

    features.update(
        summarize(
            left_hip_velocity,
            "left_hip_velocity"
        )
    )

    features.update(
        summarize(
            right_hip_velocity,
            "right_hip_velocity"
        )
    )

    features.update(
        summarize(
            torso_velocity,
            "torso_velocity"
        )
    )


    # -----------------------------------------------------
    # DEPTH FEATURES
    # -----------------------------------------------------

    features["left_knee_flexion_depth"] = (
        180 -
        np.min(left_knee_angles)
    )

    features["right_knee_flexion_depth"] = (
        180 -
        np.min(right_knee_angles)
    )

    features["left_hip_flexion_depth"] = (
        180 -
        np.min(left_hip_angles)
    )

    features["right_hip_flexion_depth"] = (
        180 -
        np.min(right_hip_angles)
    )

    features["maximum_torso_lean"] = (
        np.max(torso_angles)
    )


    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    features["subject_id"] = subject_id

    features["repetition"] = repetition

    features["is_correct"] = bool(
        group["is_correct"].iloc[0]
    )


    all_features.append(features)


# ---------------------------------------------------------
# CREATE FINAL FEATURE DATASET
# ---------------------------------------------------------

feature_df = pd.DataFrame(
    all_features
)

print()
print(
    "Feature dataset shape:",
    feature_df.shape
)

print(
    "Correct repetitions:",
    int(
        feature_df["is_correct"].sum()
    )
)

print(
    "Incorrect repetitions:",
    int(
        (~feature_df["is_correct"]).sum()
    )
)

print(
    "Number of ML features:",
    len(feature_df.columns) - 3
)


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

feature_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print(
    "Saved improved squat features to:"
)

print(OUTPUT_FILE)