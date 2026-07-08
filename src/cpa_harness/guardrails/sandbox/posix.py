"""POSIX sandbox (Linux/macOS): chdir + rlimit + env cleanup."""
import os
import re
import subprocess
import time

from cpa_harness.guardrails.sandbox.backend import SandboxResult, SandboxBackend

try:
    import resource
    _HAS_RESOURCE = True
except ImportError:
    resource = None  # type: ignore[assignment]
    _HAS_RESOURCE = False

# env vars whose names look like secrets/tokens — drop from child env
_SECRET_VAR_RE = re.compile(r".*(KEY|TOKEN|SECRET|PASSWORD|CRED).*", re.IGNORECASE)


def _safe_environ() -> dict[str, str]:
    """Return a copy of os.environ with secret-looking vars removed."""
    return {k: v for k, v in os.environ.items() if not _SECRET_VAR_RE.match(k)}


def _limit_resources() -> None:
    """Set resource limits on the child: 5s CPU, 256MB virtual memory."""
    if not _HAS_RESOURCE:
        return
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)


class PosixSandbox(SandboxBackend):
    def __init__(self, workspace: str):
        self.workspace = workspace

    def run(self, tool: str, args: dict, cwd: str) -> SandboxResult:
        if tool == "exec_command":
            return self._exec(args["cmd"], cwd)
        raise NotImplementedError(f"POSIX sandbox does not support tool {tool!r}")

    def _exec(self, cmd: str, cwd: str) -> SandboxResult:
        start = time.time()
        kwargs: dict = dict(
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_safe_environ(),
            text=True,
        )
        if _HAS_RESOURCE:
            kwargs["preexec_fn"] = _limit_resources
        proc = subprocess.Popen(cmd, **kwargs)
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        duration = int((time.time() - start) * 1000)
        return SandboxResult(
            stdout=stdout or "",
            stderr=stderr or "",
            exit_code=proc.returncode if proc.returncode >= 0 else None,
            signal=-proc.returncode if proc.returncode < 0 else None,
            duration_ms=duration,
        )
