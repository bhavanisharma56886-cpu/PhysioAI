from ai.analysis.sensor_processor import create_sensor_data


def test_sensor_data():
    raw_data = {
        "timestamp": 0.10,

        "acc_x": 0.12,
        "acc_y": 0.25,
        "acc_z": 9.81,

        "gyro_x": 0.01,
        "gyro_y": 0.02,
        "gyro_z": 0.03,
    }

    sensor = create_sensor_data(raw_data)

    print("Sensor data:")
    print(sensor)

    print("\nIndividual values:")
    print("Timestamp:", sensor.timestamp)
    print("Acceleration:", sensor.acc_x, sensor.acc_y, sensor.acc_z)
    print("Gyroscope:", sensor.gyro_x, sensor.gyro_y, sensor.gyro_z)


if __name__ == "__main__":
    test_sensor_data()