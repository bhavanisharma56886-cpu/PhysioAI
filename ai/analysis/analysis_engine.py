from ai.analysis.pose_processor import process_pose
from ai.analysis.repetition_counter import RepetitionCounter
from ai.analysis.rom import get_rom_details


class AnalysisEngine:
    """
    Coordinates pose processing, repetition counting,
    and ROM calculation for an exercise session.
    """

    def __init__(self, exercise_name):
        self.exercise_name = exercise_name

        self.repetition_counter = RepetitionCounter(
            exercise_name
        )

        self.repetitions = []

    def process_frame(self, pose_data):
        """
        Process one pose frame.

        Pipeline:
            pose → angle → repetition counter
        """

        pose_result = process_pose(
            pose_data,
            self.exercise_name
        )

        # Invalid pose/keypoints
        if not pose_result["valid"]:
            return {
                "valid": False,
                "reason": pose_result["reason"],
                "repetitions": self.repetition_counter.repetition_count,
            }

        angle = pose_result["angle"]

        counter_result = self.repetition_counter.update(
            angle
        )

        # Check whether a repetition was completed
        if counter_result["completed"]:
            completed_rep = counter_result["completed_rep"]

            rom_result = get_rom_details([
                completed_rep["min_angle"],
                completed_rep["max_angle"],
            ])

            repetition_result = {
                "rep_number": completed_rep["rep_number"],
                "min_angle": completed_rep["min_angle"],
                "max_angle": completed_rep["max_angle"],
                "rom": rom_result["rom"],
            }

            self.repetitions.append(
                repetition_result
            )

            return {
                "valid": True,
                "angle": angle,
                "state": counter_result["state"],
                "repetitions": counter_result["repetitions"],
                "completed_rep": repetition_result,
            }

        return {
            "valid": True,
            "angle": angle,
            "state": counter_result["state"],
            "repetitions": counter_result["repetitions"],
            "completed_rep": None,
        }

    def get_session_summary(self):
        """
        Return the current exercise-session summary.
        """

        return {
            "exercise": self.exercise_name,
            "total_reps": self.repetition_counter.repetition_count,
            "repetitions": self.repetitions,
        }