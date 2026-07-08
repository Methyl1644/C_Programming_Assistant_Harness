"""run_feedback tool. Stub for now; real implementation in Task 11."""
from cpa_harness.observation import Observation


def run(args: dict, cwd: str) -> Observation:
    return Observation(
        tool="run_feedback",
        result="run_feedback not yet implemented (Task 11)",
        exit_code=0,
    )
