from dataclasses import dataclass


@dataclass
class SensorData:
    """
    Represents one MPU6050 sensor reading.
    """

    timestamp: float

    acc_x: float
    acc_y: float
    acc_z: float

    gyro_x: float
    gyro_y: float
    gyro_z: float


def create_sensor_data(data):
    """
    Convert a raw sensor dictionary into a SensorData object.

    Expected input:

    {
        "timestamp": 0.10,
        "acc_x": 0.1,
        "acc_y": 0.2,
        "acc_z": 9.8,
        "gyro_x": 0.01,
        "gyro_y": 0.02,
        "gyro_z": 0.03
    }
    """

    required_fields = [
        "timestamp",
        "acc_x",
        "acc_y",
        "acc_z",
        "gyro_x",
        "gyro_y",
        "gyro_z",
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(
                f"Missing sensor field: {field}"
            )

    return SensorData(
        timestamp=float(data["timestamp"]),

        acc_x=float(data["acc_x"]),
        acc_y=float(data["acc_y"]),
        acc_z=float(data["acc_z"]),

        gyro_x=float(data["gyro_x"]),
        gyro_y=float(data["gyro_y"]),
        gyro_z=float(data["gyro_z"]),
    )