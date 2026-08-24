import math

from ai.analysis.analysis_engine import AnalysisEngine


def create_pose(angle):
    """
    Create test keypoints that produce the requested
    elbow angle.

    Shoulder is fixed at (0, 1).
    Elbow is fixed at (0, 0).
    Wrist is positioned mathematically.
    """

    # Shoulder direction from elbow is 90 degrees.
    shoulder_direction = 90

    # Position wrist so the angle between
    # shoulder-elbow and wrist-elbow equals
    # the requested angle.
    wrist_direction = shoulder_direction - angle

    wrist_x = math.cos(math.radians(wrist_direction))
    wrist_y = math.sin(math.radians(wrist_direction))

    return {
        "shoulder": {
            "x": 0,
            "y": 1,
            "confidence": 0.98,
        },

        "elbow": {
            "x": 0,
            "y": 0,
            "confidence": 0.98,
        },

        "wrist": {
            "x": wrist_x,
            "y": wrist_y,
            "confidence": 0.98,
        },
    }


def test_analysis_engine():

    engine = AnalysisEngine("bicep_curl")

    angles = [
        165,
        140,
        100,
        70,
        55,
        90,
        130,
        165,
    ]

    for index, expected_angle in enumerate(angles):

        keypoints = create_pose(expected_angle)

        pose_data = {
            "timestamp": index * 0.1,
            "keypoints": keypoints,
        }

        result = engine.process_frame(pose_data)

        print(
            f"Frame {index + 1}: "
            f"Expected={expected_angle}° | "
            f"Calculated={result.get('angle'):.2f}° | "
            f"State={result.get('state')} | "
            f"Reps={result.get('repetitions')}"
        )

        if result.get("completed_rep"):
            print(
                "  → Completed:",
                result["completed_rep"]
            )

    print("\nSession summary:")
    print(engine.get_session_summary())


if __name__ == "__main__":
    test_analysis_engine()