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
    """Parse gcc's 'file:line:col: severity: msg' format.

    Returns the first error, the first warning if no errors, or None.
    Short-circuits on the first error so we don't accumulate the rest
    (no caller cares about subsequent errors when one is fatal).
    """
    first_warning: FeedbackReport | None = None
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
            return report
        if first_warning is None:
            first_warning = report
    return first_warning
