"""Parse gcc error output into a structured FeedbackReport.

gcc output format:
   <filename>:<line>:<col>: <severity>: <message>
"""
import re
from cpa_harness.feedback.report import FeedbackReport

_GCC_LINE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+):\s+"
    r"(?P<severity>error|warning|note):\s+(?P<msg>.+)$"
)


def parse_gcc(stderr: str, file: str = "") -> FeedbackReport | None:
    errors: list[FeedbackReport] = []
    warnings: list[FeedbackReport] = []
    for line in stderr.splitlines():
        m = _GCC_LINE.match(line)
        if not m:
            continue
        severity = m["severity"]
        if severity == "note":
            continue
        report = FeedbackReport(
            verdict="CE",
            file=m["file"],
            line=int(m["line"]),
            col=int(m["col"]),
            severity=severity,
            msg=m["msg"],
        )
        if severity == "error":
            errors.append(report)
        elif severity == "warning":
            warnings.append(report)
    if errors:
        return errors[0]
    if warnings:
        return warnings[0]
    return None
