import cv2
from ultralytics import YOLO

# -----------------------------------------
# 1. Load YOLO-Pose model
# -----------------------------------------
model = YOLO("yolo11n-pose.pt")


# -----------------------------------------
# 2. Open the webcam
# -----------------------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()


# -----------------------------------------
# 3. Start reading camera frames
# -----------------------------------------
while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera frame.")
        break


    # -----------------------------------------
    # 4. Detect pose using YOLO-Pose
    # -----------------------------------------
    results = model(frame, verbose=False)

    result = results[0]


    # -----------------------------------------
    # 5. Check whether a person was detected
    # -----------------------------------------
    if result.keypoints is not None and len(result.keypoints.xy) > 0:

        # Get coordinates of the first detected person
        points = result.keypoints.xy[0]

        # Get confidence values of the first detected person
        confidence = result.keypoints.conf[0]


        # -----------------------------------------
        # 6. Extract required keypoints
        # -----------------------------------------

        # Left Shoulder = keypoint 5
        shoulder = points[5]
        shoulder_conf = confidence[5]

        # Left Elbow = keypoint 7
        elbow = points[7]
        elbow_conf = confidence[7]

        # Left Wrist = keypoint 9
        wrist = points[9]
        wrist_conf = confidence[9]


        # -----------------------------------------
        # 7. Print coordinates + confidence
        # -----------------------------------------
        print("----------------------------------------")

        print(
            f"Shoulder: "
            f"x={shoulder[0].item():.1f}, "
            f"y={shoulder[1].item():.1f}, "
            f"confidence={shoulder_conf.item():.2f}"
        )

        print(
            f"Elbow:    "
            f"x={elbow[0].item():.1f}, "
            f"y={elbow[1].item():.1f}, "
            f"confidence={elbow_conf.item():.2f}"
        )

        print(
            f"Wrist:    "
            f"x={wrist[0].item():.1f}, "
            f"y={wrist[1].item():.1f}, "
            f"confidence={wrist_conf.item():.2f}"
        )


    # -----------------------------------------
    # 8. Show camera
    # -----------------------------------------
    cv2.imshow("YOLO-Pose Keypoint Test", frame)


    # -----------------------------------------
    # 9. Press Q to stop
    # -----------------------------------------
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# -----------------------------------------
# 10. Close everything
# -----------------------------------------
cap.release()
cv2.destroyAllWindows()

print("Keypoint test stopped.")