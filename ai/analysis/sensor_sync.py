from bisect import bisect_left


def find_closest_sensor_reading(camera_timestamp, sensor_data):
    """
    Find the sensor reading closest to a camera-frame timestamp.

    Parameters:
        camera_timestamp: Timestamp of the camera frame.
        sensor_data: List of SensorData objects sorted by timestamp.

    Returns:
        The closest SensorData object, or None if the list is empty.
    """

    if not sensor_data:
        return None

    timestamps = [
        sensor.timestamp
        for sensor in sensor_data
    ]

    position = bisect_left(
        timestamps,
        camera_timestamp
    )

    # Camera timestamp is before the first sensor reading
    if position == 0:
        return sensor_data[0]

    # Camera timestamp is after the last sensor reading
    if position == len(sensor_data):
        return sensor_data[-1]

    before = sensor_data[position - 1]
    after = sensor_data[position]

    before_difference = abs(
        before.timestamp - camera_timestamp
    )

    after_difference = abs(
        after.timestamp - camera_timestamp
    )

    if before_difference <= after_difference:
        return before

    return after


def synchronize_frame(camera_frame, sensor_data):
    """
    Combine a camera frame with its closest sensor reading.

    Returns a dictionary containing both sources.
    """

    sensor = find_closest_sensor_reading(
        camera_frame["timestamp"],
        sensor_data
    )

    return {
        "camera": camera_frame,
        "sensor": sensor,
    }