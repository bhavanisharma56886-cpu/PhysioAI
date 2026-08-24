from ai.analysis.exercise_config import get_exercise_config


class RepetitionCounter:
    """
    Counts exercise repetitions using joint-angle movement.

    State flow:

        READY
          ↓
      CONTRACTING
          ↓
         PEAK
          ↓
      RETURNING
          ↓
      COMPLETED → rep + 1
    """

    def __init__(self, exercise_name):
        self.exercise_name = exercise_name
        self.config = get_exercise_config(exercise_name)

        self.state = "READY"
        self.repetition_count = 0

        self.current_min_angle = None
        self.current_max_angle = None

    def update(self, angle):
        """
        Process one new angle value.

        Returns a dictionary containing the current state.
        If a repetition is completed, the result also contains
        the completed repetition's angle information.
        """

        if angle is None:
            return self.get_status()

        contraction_angle = self.config["contraction_angle"]
        return_angle = self.config["return_angle"]

        # Track minimum and maximum angle
        if self.current_min_angle is None:
            self.current_min_angle = angle
            self.current_max_angle = angle
        else:
            self.current_min_angle = min(
                self.current_min_angle,
                angle
            )

            self.current_max_angle = max(
                self.current_max_angle,
                angle
            )

        # READY → CONTRACTING
        if self.state == "READY":
            if angle < return_angle:
                self.state = "CONTRACTING"

        # CONTRACTING → PEAK
        elif self.state == "CONTRACTING":
            if angle <= contraction_angle:
                self.state = "PEAK"

        # PEAK → RETURNING
        elif self.state == "PEAK":
            if angle > contraction_angle:
                self.state = "RETURNING"

        # RETURNING → COMPLETED
        elif self.state == "RETURNING":
            if angle >= return_angle:

                completed_rep = {
                    "rep_number": self.repetition_count + 1,
                    "min_angle": self.current_min_angle,
                    "max_angle": self.current_max_angle,
                }

                self.repetition_count += 1
                self.state = "READY"

                # Reset for the next repetition
                self.current_min_angle = None
                self.current_max_angle = None

                return {
                    **self.get_status(),
                    "completed": True,
                    "completed_rep": completed_rep,
                }

        return {
            **self.get_status(),
            "completed": False,
        }

    def get_status(self):
        """
        Return the current counter status.
        """

        return {
            "exercise": self.exercise_name,
            "state": self.state,
            "repetitions": self.repetition_count,
            "min_angle": self.current_min_angle,
            "max_angle": self.current_max_angle,
        }