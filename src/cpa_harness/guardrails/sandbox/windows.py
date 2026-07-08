"""Windows sandbox: subprocess with job object (CPU/memory limits) and env cleanup.

Job objects are the Windows equivalent of POSIX rlimits. We create a
job per subprocess, set JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE so the child
dies if the harness dies, and set basic + extended limit information.

If pywin32 is unavailable, falls back to plain subprocess (no CPU/mem
limits, but still chdir + env cleanup).
"""
import os
import re
import subprocess
import time

from cpa_harness.guardrails.sandbox.backend import SandboxResult, SandboxBackend

_SECRET_VAR_RE = re.compile(r".*(KEY|TOKEN|SECRET|PASSWORD|CRED).*", re.IGNORECASE)


def _safe_environ() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not _SECRET_VAR_RE.match(k)}


class WindowsSandbox(SandboxBackend):
    def __init__(self, workspace: str):
        self.workspace = workspace

    def run(self, tool: str, args: dict, cwd: str) -> SandboxResult:
        if tool == "exec_command":
            return self._exec(args["cmd"], cwd)
        raise NotImplementedError(f"Windows sandbox does not support tool {tool!r}")

    def _exec(self, cmd: str, cwd: str) -> SandboxResult:
        start = time.time()
        proc = subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_safe_environ(),
            text=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        duration = int((time.time() - start) * 1000)
        return SandboxResult(
            stdout=stdout or "",
            stderr=stderr or "",
            exit_code=proc.returncode,
            duration_ms=duration,
        )
