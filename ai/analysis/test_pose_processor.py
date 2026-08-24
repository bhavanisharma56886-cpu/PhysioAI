from ai.analysis.pose_processor import process_pose


def test_bicep_curl_pose():
    pose_data = {
        "timestamp": 0.10,
        "keypoints": {
            "shoulder": {
                "x": 0,
                "y": 1,
                "confidence": 0.98
            },
            "elbow": {
                "x": 0,
                "y": 0,
                "confidence": 0.97
            },
            "wrist": {
                "x": 1,
                "y": 0,
                "confidence": 0.96
            },

            # Extra keypoints are intentionally included.
            # Our processor should simply ignore them
            # because Bicep Curl only needs 3 joints.
            "hip": {
                "x": 2,
                "y": 2,
                "confidence": 0.95
            },
            "knee": {
                "x": 2,
                "y": 3,
                "confidence": 0.94
            },
            "ankle": {
                "x": 2,
                "y": 4,
                "confidence": 0.93
            }
        }
    }

    result = process_pose(
        pose_data,
        "bicep_curl"
    )

    print("Processing result:")
    print(result)


if __name__ == "__main__":
    test_bicep_curl_pose()