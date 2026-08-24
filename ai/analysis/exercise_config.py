EXERCISE_CONFIG = {
    "bicep_curl": {
        "name": "Bicep Curl",

        # Joints used to calculate the main angle
        "angle_joints": ("shoulder", "elbow", "wrist"),

        # Bicep curl: angle becomes smaller during contraction
        "movement": "decreasing_then_increasing",

        # These are starting values for software testing.
        # They must be tested and adjusted using real pose data.
        "contraction_angle": 70,
        "return_angle": 150,
    },

    "squat": {
        "name": "Squat",
        "angle_joints": ("hip", "knee", "ankle"),

        "movement": "decreasing_then_increasing",

        "contraction_angle": 90,
        "return_angle": 160,
    },

    "knee_extension": {
        "name": "Knee Extension",
        "angle_joints": ("hip", "knee", "ankle"),

        "movement": "decreasing_then_increasing",

        "contraction_angle": 90,
        "return_angle": 160,
    },

    "shoulder_raise": {
        "name": "Shoulder Raise",
        "angle_joints": ("shoulder", "elbow", "wrist"),

        "movement": "decreasing_then_increasing",

        "contraction_angle": 70,
        "return_angle": 150,
    },
}


def get_exercise_config(exercise_name):
    """
    Return the configuration for a selected exercise.
    """

    exercise_name = exercise_name.lower().strip()

    if exercise_name not in EXERCISE_CONFIG:
        raise ValueError(f"Unsupported exercise: {exercise_name}")

    return EXERCISE_CONFIG[exercise_name]