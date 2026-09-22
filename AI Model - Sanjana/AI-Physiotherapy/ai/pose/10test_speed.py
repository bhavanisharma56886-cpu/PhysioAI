import cv2
import time
from ultralytics import YOLO
from angle_utils import calculate_angle


model = YOLO("yolo11n-pose.pt")

cap = cv2.VideoCapture(0)


previous_angle = None
previous_time = None

min_angle = None
max_angle = None

reps = 0
curl_started = False

CURL_ANGLE = 80
STRAIGHT_ANGLE = 150


while True:

    ret, frame = cap.read()

    if not ret:
        print("Could not access camera.")
        break

    current_time = time.time()

    results = model(frame)

    annotated_frame = results[0].plot()

    if results[0].keypoints is not None:

        keypoints = results[0].keypoints.xy
        confidences = results[0].keypoints.conf

        if len(keypoints) > 0:

            person = keypoints[0]

            shoulder = person[5]
            elbow = person[7]
            wrist = person[9]

            shoulder_conf = float(confidences[0][5])
            elbow_conf = float(confidences[0][7])
            wrist_conf = float(confidences[0][9])

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

            if (
                shoulder_conf >= 0.5
                and elbow_conf >= 0.5
                and wrist_conf >= 0.5
            ):

                angle = calculate_angle(
                    shoulder_point,
                    elbow_point,
                    wrist_point
                )

                if angle is not None and 30 <= angle <= 180:

                    if min_angle is None or angle < min_angle:
                        min_angle = angle

                    if max_angle is None or angle > max_angle:
                        max_angle = angle

                    rom = max_angle - min_angle

                    speed = 0.0

                    if previous_angle is not None and previous_time is not None:

                        time_difference = current_time - previous_time

                        if time_difference > 0:

                            angle_difference = abs(
                                angle - previous_angle
                            )

                            speed = angle_difference / time_difference

                    previous_angle = angle
                    previous_time = current_time

                    if angle <= CURL_ANGLE:

                        curl_started = True

                    if angle >= STRAIGHT_ANGLE and curl_started:

                        reps += 1

                        curl_started = False

                        print(
                            f"REPETITION COMPLETED: {reps}"
                        )

                    print(
                        f"Angle: {angle:.2f}° | "
                        f"ROM: {rom:.2f}° | "
                        f"Speed: {speed:.2f} deg/s | "
                        f"Reps: {reps}"
                    )

                    cv2.putText(
                        annotated_frame,
                        f"Elbow Angle: {angle:.1f} deg",
                        (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        annotated_frame,
                        f"ROM: {rom:.1f} deg",
                        (20, 65),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        annotated_frame,
                        f"Speed: {speed:.1f} deg/s",
                        (20, 95),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        annotated_frame,
                        f"Reps: {reps}",
                        (20, 125),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                    if curl_started:

                        cv2.putText(
                            annotated_frame,
                            "Curl Position",
                            (20, 155),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            2
                        )

                    else:

                        cv2.putText(
                            annotated_frame,
                            "Ready",
                            (20, 155),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )

                else:

                    cv2.putText(
                        annotated_frame,
                        "Unreliable angle",
                        (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

            else:

                cv2.putText(
                    annotated_frame,
                    "Low pose confidence",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

    cv2.imshow(
        "Bicep Curl - Speed Test",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()


print("\nFinal Results")
print("-------------------------")
print(f"Total Repetitions: {reps}")

if min_angle is not None and max_angle is not None:

    final_rom = max_angle - min_angle

    print(f"Minimum Angle: {min_angle:.2f}°")
    print(f"Maximum Angle: {max_angle:.2f}°")
    print(f"ROM: {final_rom:.2f}°")

else:

    print("No valid angle data collected.")