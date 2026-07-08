"""FeedbackRunner: orchestrate gcc + valgrind for a target.

Strategy:
  1. If target file doesn't exist, return AC
  2. Run `gcc -Wall -Werror <target> -o <target>.out` via sandbox
  3. If compile fails, parse with parse_gcc -> CE
  4. If compile succeeds, run `valgrind --error-exitcode=1 ./<target>.out`
  5. If valgrind reports leak, parse -> MLE
  6. Otherwise AC
"""
from pathlib import Path

from cpa_harness.feedback.gcc_parser import parse_gcc
from cpa_harness.feedback.report import FeedbackReport
from cpa_harness.feedback.valgrind_parser import parse_valgrind
from cpa_harness.guardrails.sandbox.backend import SandboxBackend


def run_feedback(target: str, cwd: str, sandbox: SandboxBackend) -> FeedbackReport:
    src = Path(cwd) / target
    if not src.exists():
        return FeedbackReport(verdict="AC", file=target, msg="no file")

    out = f"{target}.out"
    compile_result = sandbox.run(
        "exec_command",
        {"cmd": f"gcc -Wall -Werror {target} -o {out}"},
        cwd=cwd,
    )
    if compile_result.exit_code != 0:
        report = parse_gcc(compile_result.stderr, file=target)
        if report is not None:
            return report
        return FeedbackReport(
            verdict="CE", file=target,
            msg=compile_result.stderr[:500] or "compilation failed",
        )

    valgrind_result = sandbox.run(
        "exec_command",
        {"cmd": f"valgrind --error-exitcode=1 ./{out}"},
        cwd=cwd,
    )
    leak = parse_valgrind(valgrind_result.stderr, file=target)
    if leak is not None:
        return leak

    return FeedbackReport(verdict="AC", file=target, msg="compiled and ran clean")
