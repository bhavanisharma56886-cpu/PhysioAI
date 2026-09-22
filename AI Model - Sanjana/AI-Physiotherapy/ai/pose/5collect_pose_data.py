import cv2
import csv
from datetime import datetime
from ultralytics import YOLO


# -----------------------------
# 1. Load YOLO-Pose model
# -----------------------------
model = YOLO("yolo11n-pose.pt")


# -----------------------------
# 2. Open camera
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()


# -----------------------------
# 3. Create CSV file
# -----------------------------
csv_file = "data/raw/pose/bicep_curl_pose_001.csv"

with open(csv_file, mode="w", newline="") as file:

    writer = csv.writer(file)

    # CSV column names
    writer.writerow([
        "timestamp",
        "shoulder_x",
        "shoulder_y",
        "shoulder_conf",
        "elbow_x",
        "elbow_y",
        "elbow_conf",
        "wrist_x",
        "wrist_y",
        "wrist_conf"
    ])

    print("CSV file created successfully.")
    print("Starting pose data collection...")
    print("Perform your bicep curl slowly.")
    print("Press Q to stop.")
    print("----------------------------------------")


    # -----------------------------
    # 4. Start collecting data
    # -----------------------------
    while True:

        ret, frame = cap.read()

        if not ret:
            print("ERROR: Could not read camera frame.")
            break


        # Run YOLO-Pose
        results = model(frame, verbose=False)

        result = results[0]


        # Check if keypoints were detected
        if result.keypoints is not None and len(result.keypoints.xy) > 0:

            points = result.keypoints.xy[0]
            confidence = result.keypoints.conf[0]


            # Left shoulder
            shoulder = points[5]
            shoulder_conf = confidence[5]


            # Left elbow
            elbow = points[7]
            elbow_conf = confidence[7]


            # Left wrist
            wrist = points[9]
            wrist_conf = confidence[9]


            # Current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


            # Save data into CSV
            writer.writerow([
                timestamp,
                shoulder[0].item(),
                shoulder[1].item(),
                shoulder_conf.item(),
                elbow[0].item(),
                elbow[1].item(),
                elbow_conf.item(),
                wrist[0].item(),
                wrist[1].item(),
                wrist_conf.item()
            ])


            # Show data in terminal
            print(
                f"Shoulder: ({shoulder[0].item():.1f}, {shoulder[1].item():.1f}) "
                f"Conf: {shoulder_conf.item():.2f}"
            )

            print(
                f"Elbow:    ({elbow[0].item():.1f}, {elbow[1].item():.1f}) "
                f"Conf: {elbow_conf.item():.2f}"
            )

            print(
                f"Wrist:    ({wrist[0].item():.1f}, {wrist[1].item():.1f}) "
                f"Conf: {wrist_conf.item():.2f}"
            )

            print("----------------------------------------")


        # Show camera
        cv2.imshow("Pose Data Collection", frame)


        # Press Q to stop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# -----------------------------
# 5. Close everything
# -----------------------------
cap.release()
cv2.destroyAllWindows()

print("Pose data collection stopped.")
print(f"Data saved to: {csv_file}")