"""In-memory sandbox for tests: pre-programmed responses, no real subprocess."""
from cpa_harness.guardrails.sandbox.backend import SandboxResult, SandboxBackend


class InMemorySandbox(SandboxBackend):
    def __init__(self, responses: dict | None = None):
        self.responses = responses or {}
        self.calls: list[tuple[str, dict, str]] = []

    def run(self, tool: str, args: dict, cwd: str) -> SandboxResult:
        self.calls.append((tool, args, cwd))
        if tool in self.responses:
            return self.responses[tool]
        return SandboxResult(stdout="", stderr="", exit_code=0)
