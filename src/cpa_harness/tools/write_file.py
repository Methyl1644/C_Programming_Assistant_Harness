"""write_file tool. Caller (loop) is responsible for HITL approval."""
from pathlib import Path
from cpa_harness.observation import Observation


def run(args: dict, cwd: str) -> Observation:
    path = Path(cwd) / args["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args["content"], encoding="utf-8")
    return Observation(
        tool="write_file",
        result=f"wrote {len(args['content'])} bytes to {path}",
        exit_code=0,
    )
