"""Sandbox backend protocol."""
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int | None = None
    signal: int | None = None
    duration_ms: int = 0


@runtime_checkable
class SandboxBackend(Protocol):
    def run(self, tool: str, args: dict, cwd: str) -> SandboxResult:
        """Run a tool inside the sandbox; return its result."""
        ...
