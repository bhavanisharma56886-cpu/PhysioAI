from ai.analysis.sensor_processor import create_sensor_data
from ai.analysis.sensor_sync import (
    find_closest_sensor_reading,
    synchronize_frame,
)


def test_sensor_sync():

    sensor_data = [
        create_sensor_data({
            "timestamp": 9.98,
            "acc_x": 0.1,
            "acc_y": 0.2,
            "acc_z": 9.8,
            "gyro_x": 0.01,
            "gyro_y": 0.02,
            "gyro_z": 0.03,
        }),

        create_sensor_data({
            "timestamp": 10.06,
            "acc_x": 0.2,
            "acc_y": 0.3,
            "acc_z": 9.7,
            "gyro_x": 0.02,
            "gyro_y": 0.03,
            "gyro_z": 0.04,
        }),

        create_sensor_data({
            "timestamp": 10.18,
            "acc_x": 0.3,
            "acc_y": 0.4,
            "acc_z": 9.6,
            "gyro_x": 0.03,
            "gyro_y": 0.04,
            "gyro_z": 0.05,
        }),

        create_sensor_data({
            "timestamp": 10.25,
            "acc_x": 0.4,
            "acc_y": 0.5,
            "acc_z": 9.5,
            "gyro_x": 0.04,
            "gyro_y": 0.05,
            "gyro_z": 0.06,
        }),
    ]

    camera_frames = [
        {
            "timestamp": 10.00,
            "angle": 165,
        },
        {
            "timestamp": 10.10,
            "angle": 120,
        },
        {
            "timestamp": 10.20,
            "angle": 70,
        },
    ]

    for frame in camera_frames:

        closest = find_closest_sensor_reading(
            frame["timestamp"],
            sensor_data,
        )

        print(
            f"Camera: {frame['timestamp']:.2f}s "
            f"→ Sensor: {closest.timestamp:.2f}s"
        )

        combined = synchronize_frame(
            frame,
            sensor_data,
        )

        print(
            f"  Angle: {combined['camera']['angle']}° | "
            f"Sensor timestamp: "
            f"{combined['sensor'].timestamp:.2f}s"
        )


if __name__ == "__main__":
    test_sensor_sync()