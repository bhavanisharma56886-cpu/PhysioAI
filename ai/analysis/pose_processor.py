from ai.analysis.exercise_config import get_exercise_config
from ai.utils.angle import calculate_angle


def process_pose(pose_data, exercise_name):
    """
    Process one pose frame for the selected exercise.

    Parameters:
        pose_data: Dictionary containing timestamp and keypoints.
        exercise_name: Name of the exercise.

    Returns:
        Dictionary containing the selected joints and calculated angle.
    """

    config = get_exercise_config(exercise_name)
    joint_names = config["angle_joints"]

    keypoints = pose_data.get("keypoints", {})

    selected_points = {}

    for joint_name in joint_names:
        if joint_name not in keypoints:
            return {
                "timestamp": pose_data.get("timestamp"),
                "exercise": exercise_name,
                "valid": False,
                "reason": f"Missing keypoint: {joint_name}",
            }

        point = keypoints[joint_name]

        confidence = point.get("confidence", 1.0)

        if confidence <= 0:
            return {
                "timestamp": pose_data.get("timestamp"),
                "exercise": exercise_name,
                "valid": False,
                "reason": f"Invalid confidence for: {joint_name}",
            }

        selected_points[joint_name] = (
            point["x"],
            point["y"]
        )

    point_a = selected_points[joint_names[0]]
    point_b = selected_points[joint_names[1]]
    point_c = selected_points[joint_names[2]]

    angle = calculate_angle(
        point_a,
        point_b,
        point_c
    )

    if angle is None:
        return {
            "timestamp": pose_data.get("timestamp"),
            "exercise": exercise_name,
            "valid": False,
            "reason": "Unable to calculate angle",
        }

    return {
        "timestamp": pose_data.get("timestamp"),
        "exercise": exercise_name,
        "valid": True,
        "joints": selected_points,
        "angle": angle,
    }