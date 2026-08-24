from ai.analysis.repetition_counter import RepetitionCounter


def test_bicep_curls():
    counter = RepetitionCounter("bicep_curl")

    angles = [
        # Rep 1
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 2
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 3
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 4
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 5
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 6
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 7
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 8
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 9
        165, 140, 100, 70, 55, 90, 130, 165,

        # Rep 10
        165, 140, 100, 70, 55, 90, 130, 165,
    ]

    for angle in angles:
        status = counter.update(angle)

        print(
            f"Angle: {angle:>3}° | "
            f"State: {status['state']:<11} | "
            f"Reps: {status['repetitions']}"
        )

        if status["completed"]:
            rep = status["completed_rep"]

            print(
                f"  → Rep {rep['rep_number']} completed | "
                f"Min: {rep['min_angle']}° | "
                f"Max: {rep['max_angle']}°"
            )

    print("\nFinal result:")
    print("Repetitions:", counter.repetition_count)


if __name__ == "__main__":
    test_bicep_curls()