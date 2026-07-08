"""FeedbackReport: structured parse of gcc/valgrind/test output."""
from typing import Literal
from pydantic import BaseModel

Verdict = Literal["AC", "CE", "WA", "TLE", "MLE", "RE"]


class FeedbackReport(BaseModel):
    verdict: Verdict
    file: str
    line: int | None = None
    col: int | None = None
    severity: Literal["error", "warning"] | None = None
    msg: str
    snippet: str | None = None
    expected: str | None = None
    actual: str | None = None
    signal_name: str | None = None
    rss_mb: float | None = None
    leak_summary: str | None = None
