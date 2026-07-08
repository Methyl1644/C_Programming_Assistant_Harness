"""run_feedback tool. Delegates to FeedbackRunner."""
from cpa_harness.observation import Observation
from cpa_harness.guardrails.sandbox.backend import SandboxBackend
from cpa_harness.feedback.runner import run_feedback as _run


def run(args: dict, cwd: str, sandbox: SandboxBackend) -> Observation:
    target = args.get("target") or args.get("path", "")
    report = _run(target=target, cwd=cwd, sandbox=sandbox)
    return Observation(
        tool="run_feedback",
        result=f"{report.verdict}: {report.msg}",
        exit_code=0,
        feedback=report,
    )
