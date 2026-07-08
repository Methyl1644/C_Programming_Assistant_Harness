"""finish_tutoring tool. Signals the loop to exit successfully."""
from cpa_harness.observation import Observation


def run(args: dict, cwd: str) -> Observation:
    return Observation(tool="finish_tutoring", result=args.get("summary", ""), exit_code=0)
