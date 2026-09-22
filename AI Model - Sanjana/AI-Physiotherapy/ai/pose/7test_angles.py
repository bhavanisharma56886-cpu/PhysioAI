import cv2
from ultralytics import YOLO
from angle_utils import calculate_angle


model = YOLO("yolo11n-pose.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not access camera.")
        break

    results = model(frame)

    annotated_frame = results[0].plot()

    if results[0].keypoints is not None:
        keypoints = results[0].keypoints.xy

        if len(keypoints) > 0:
            person = keypoints[0]

            shoulder = person[5]
            elbow = person[7]
            wrist = person[9]

            shoulder_point = (
                float(shoulder[0]),
                float(shoulder[1])
            )

            elbow_point = (
                float(elbow[0]),
                float(elbow[1])
            )

            wrist_point = (
                float(wrist[0]),
                float(wrist[1])
            )

            angle = calculate_angle(
                shoulder_point,
                elbow_point,
                wrist_point
            )

            if angle is not None:

                print(f"Elbow Angle: {angle:.2f} degrees")

                cv2.putText(
                    annotated_frame,
                    f"Elbow Angle: {angle:.1f} deg",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

    cv2.imshow("Bicep Curl - Elbow Angle", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()