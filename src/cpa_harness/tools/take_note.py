"""take_note tool. Stub; loop layer handles persistence."""
from cpa_harness.observation import Observation


def run(args: dict, cwd: str) -> Observation:
    return Observation(tool="take_note", result=f"noted: {args['note']}", exit_code=0)
