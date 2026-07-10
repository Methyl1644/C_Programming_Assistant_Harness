import os
import sys
import pytest
from cpa_harness.guardrails.sandbox.posix import PosixSandbox


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only")
def test_echo_command_runs():
    sb = PosixSandbox(workspace="/tmp")
    r = sb.run("exec_command", {"cmd": "echo hello"}, cwd="/tmp")
    assert r.exit_code == 0
    assert r.stdout.strip() == "hello"


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only")
def test_sandbox_clears_secret_env(monkeypatch):
    sb = PosixSandbox(workspace="/tmp")
    secret_value = "sk-supersecret-12345"
    monkeypatch.setenv("OPENAI_API_KEY", secret_value)
    r = sb.run("exec_command",
               {"cmd": "echo OPENAI_KEY=$OPENAI_API_KEY"},
               cwd="/tmp")
    assert secret_value not in r.stdout, "secret leaked into child env"
    assert r.stdout.strip() == "OPENAI_KEY="


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only")
def test_sandbox_clears_token_env(monkeypatch):
    sb = PosixSandbox(workspace="/tmp")
    monkeypatch.setenv("MY_TOKEN", "leakable")
    r = sb.run("exec_command",
               {"cmd": "echo TOKEN=$MY_TOKEN"},
               cwd="/tmp")
    assert "leakable" not in r.stdout


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only")
def test_sandbox_runs_in_workspace(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    sb = PosixSandbox(workspace=str(workspace))
    r = sb.run("exec_command", {"cmd": "pwd"}, cwd=str(workspace))
    assert r.stdout.strip() == str(workspace)


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only")
def test_sandbox_captures_nonzero_exit():
    sb = PosixSandbox(workspace="/tmp")
    r = sb.run("exec_command", {"cmd": "false"}, cwd="/tmp")
    assert r.exit_code == 1


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only")
def test_sandbox_captures_signal():
    sb = PosixSandbox(workspace="/tmp")
    r = sb.run("exec_command", {"cmd": "kill -SEGV $$"}, cwd="/tmp")
    assert r.signal == 11  # SIGSEGV
