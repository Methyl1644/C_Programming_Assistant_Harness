"""Tests for CLI entry point."""
import subprocess
import sys
from pathlib import Path


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "cpa_harness.cli", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "run" in result.stdout
    assert "setup" in result.stdout
    assert "key" in result.stdout


def test_cli_run_with_mock_llm(tmp_path):
    (tmp_path / "main.c").write_text("int main() { return 0; }")
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "cpa_harness.cli", "run",
         "--file", str(tmp_path / "main.c"),
         "--goal", "explain",
         "--mock"],
        capture_output=True, text=True,
        cwd=repo_root,
    )
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "done" in out or "result" in out or "exit" in out
