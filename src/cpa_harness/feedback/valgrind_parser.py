"""Parse valgrind output into a structured FeedbackReport."""
import re
from cpa_harness.feedback.report import FeedbackReport

_INVALID = re.compile(r"Invalid (?:read|write) of size \d+")
_AT = re.compile(r"at 0x[0-9a-fA-F]+:\s+\S+\s+\((?P<file>[^:]+):(?P<line>\d+)\)")
_LEAK = re.compile(r"definitely lost:\s+(?P<bytes>\d+)\s+bytes")


def parse_valgrind(stderr: str, file: str = "") -> FeedbackReport | None:
    invalid = _INVALID.search(stderr)
    if invalid:
        loc = _AT.search(stderr)
        return FeedbackReport(
            verdict="MLE",
            file=loc["file"] if loc else file,
            line=int(loc["line"]) if loc else None,
            msg=invalid.group(0),
        )
    leak = _LEAK.search(stderr)
    if leak and int(leak["bytes"]) > 0:
        return FeedbackReport(
            verdict="MLE",
            file=file or "memory",
            msg=f"definitely lost {leak['bytes']} bytes",
            leak_summary=leak.group(0),
        )
    return None
