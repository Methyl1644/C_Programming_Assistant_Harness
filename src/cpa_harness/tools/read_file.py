"""read_file tool."""
from pathlib import Path
from cpa_harness.observation import Observation


def run(args: dict, cwd: str) -> Observation:
    path = Path(cwd) / args["path"]
    return Observation(
        tool="read_file",
        result=path.read_text(encoding="utf-8"),
        exit_code=0,
    )
