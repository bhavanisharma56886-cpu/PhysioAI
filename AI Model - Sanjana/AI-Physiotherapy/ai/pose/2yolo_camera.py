import cv2
from ultralytics import YOLO

# Load the YOLO-Pose model
model = YOLO("yolo11n-pose.pt")

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to access camera")
        break

    # Give the camera frame to YOLO-Pose
    results = model(frame)

    # Draw the detected pose on the frame
    annotated_frame = results[0].plot()

    # Show the result
    cv2.imshow("YOLO-Pose", annotated_frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release everything
cap.release()
cv2.destroyAllWindows()