"""list_dir tool."""
from pathlib import Path
from cpa_harness.observation import Observation


def run(args: dict, cwd: str) -> Observation:
    target = Path(cwd) / args["path"]
    entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
    return Observation(tool="list_dir", result="\n".join(entries), exit_code=0)
