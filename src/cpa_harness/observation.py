"""Observation: what happened when a tool ran."""
from pydantic import BaseModel
from cpa_harness.feedback.report import FeedbackReport


class Observation(BaseModel):
    tool: str
    result: str
    stderr: str = ""
    exit_code: int | None = None
    signal: int | None = None
    feedback: FeedbackReport | None = None
    duration_ms: int = 0

    @classmethod
    def from_sandbox_result(cls, result, tool: str) -> "Observation":
        """Build an Observation from a SandboxResult.

        Centralizes the SandboxResult -> Observation mapping so exec_command
        (and future sandbox-using tools) don't duplicate the field copying.
        Also fixes a silent bug: pre-refactor, exec_command set stderr=...
        but Observation had no stderr field, so pydantic dropped it.
        """
        return cls(
            tool=tool,
            result=result.stdout or "",
            stderr=result.stderr or "",
            exit_code=result.exit_code,
            signal=result.signal,
            duration_ms=result.duration_ms,
        )
