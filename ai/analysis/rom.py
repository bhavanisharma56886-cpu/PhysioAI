def calculate_rom(angles):
    """
    Calculate the range of motion (ROM) for one repetition.

    ROM = maximum angle - minimum angle

    Parameters:
        angles: A sequence of joint-angle values.

    Returns:
        ROM in degrees, or None if no valid angles are provided.
    """

    valid_angles = [
        angle for angle in angles
        if angle is not None
    ]

    if not valid_angles:
        return None

    minimum_angle = min(valid_angles)
    maximum_angle = max(valid_angles)

    return maximum_angle - minimum_angle


def get_rom_details(angles):
    """
    Return minimum angle, maximum angle and ROM
    for one repetition.
    """

    valid_angles = [
        angle for angle in angles
        if angle is not None
    ]

    if not valid_angles:
        return {
            "min_angle": None,
            "max_angle": None,
            "rom": None,
        }

    minimum_angle = min(valid_angles)
    maximum_angle = max(valid_angles)

    return {
        "min_angle": minimum_angle,
        "max_angle": maximum_angle,
        "rom": maximum_angle - minimum_angle,
    }