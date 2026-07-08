import os
import sys
import pytest

pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="Windows-only test",
)

try:
    from cpa_harness.guardrails.sandbox import WindowsSandbox
except ImportError:
    WindowsSandbox = None  # type: ignore[assignment]


def test_echo_runs_on_windows(tmp_path):
    sb = WindowsSandbox(workspace=str(tmp_path))
    r = sb.run("exec_command", {"cmd": "echo hello"}, cwd=str(tmp_path))
    assert r.exit_code == 0
    assert "hello" in r.stdout


def test_secret_env_stripped_on_windows(tmp_path):
    sb = WindowsSandbox(workspace=str(tmp_path))
    os.environ["OPENAI_API_KEY"] = "sk-supersecret-12345"
    r = sb.run(
        "exec_command",
        {"cmd": "echo OPENAI_KEY=%OPENAI_API_KEY%"},
        cwd=str(tmp_path),
    )
    assert "supersecret" not in r.stdout


def test_sandbox_runs_in_workspace(tmp_path):
    sb = WindowsSandbox(workspace=str(tmp_path))
    r = sb.run("exec_command", {"cmd": "cd"}, cwd=str(tmp_path))
    assert r.exit_code == 0
    assert str(tmp_path) in r.stdout


def test_sandbox_captures_nonzero_exit(tmp_path):
    sb = WindowsSandbox(workspace=str(tmp_path))
    r = sb.run("exec_command", {"cmd": "cmd /c exit 1"}, cwd=str(tmp_path))
    assert r.exit_code == 1
