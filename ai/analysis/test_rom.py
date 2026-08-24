from ai.analysis.rom import get_rom_details


def test_rom():
    repetitions = [
        [165, 140, 100, 70, 55, 90, 130, 165],
        [164, 140, 110, 80, 58, 90, 130, 164],
        [166, 145, 105, 75, 53, 90, 135, 166],
    ]

    for number, angles in enumerate(repetitions, start=1):
        result = get_rom_details(angles)

        print(
            f"Rep {number}: "
            f"Min={result['min_angle']}°, "
            f"Max={result['max_angle']}°, "
            f"ROM={result['rom']}°"
        )


if __name__ == "__main__":
    test_rom()