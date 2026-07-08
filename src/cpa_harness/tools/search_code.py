"""search_code tool: substring search across files."""
from pathlib import Path
from cpa_harness.observation import Observation


def run(args: dict, cwd: str) -> Observation:
    pattern = args["pattern"]
    target = Path(cwd) / args.get("path", ".")
    matches = []
    for p in target.rglob("*"):
        if p.is_file():
            try:
                for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if pattern in line:
                        matches.append(f"{p}:{i}:{line}")
            except (UnicodeDecodeError, OSError):
                continue
    return Observation(tool="search_code", result="\n".join(matches), exit_code=0)
