"""Tests for FeedbackRunner — orchestrates gcc + valgrind for a target."""
from cpa_harness.feedback.runner import run_feedback
from cpa_harness.guardrails.sandbox.in_memory import InMemorySandbox
from cpa_harness.guardrails.sandbox.backend import SandboxResult


def test_run_feedback_compile_error(tmp_path):
    (tmp_path / "main.c").write_text("int main() { undeclared_var; }")
    sb = InMemorySandbox(responses={
        "exec_command": SandboxResult(
            stdout="",
            stderr="main.c:1:24: error: 'undeclared_var' undeclared",
            exit_code=1,
        ),
    })
    report = run_feedback(target="main.c", cwd=str(tmp_path), sandbox=sb)
    assert report.verdict == "CE"
    assert report.line == 1


def test_run_feedback_no_target_returns_ac(tmp_path):
    sb = InMemorySandbox(responses={})
    report = run_feedback(target="missing.c", cwd=str(tmp_path), sandbox=sb)
    assert report.verdict == "AC"
