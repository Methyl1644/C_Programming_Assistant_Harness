"""Observation: what happened when a tool ran."""
from pydantic import BaseModel
from cpa_harness.feedback.report import FeedbackReport


class Observation(BaseModel):
    tool: str
    result: str
    exit_code: int | None = None
    signal: int | None = None
    feedback: FeedbackReport | None = None
    duration_ms: int = 0
