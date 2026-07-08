"""Sandbox backends for isolating tool execution."""
from cpa_harness.guardrails.sandbox.backend import SandboxResult, SandboxBackend
from cpa_harness.guardrails.sandbox.posix import PosixSandbox
from cpa_harness.guardrails.sandbox.in_memory import InMemorySandbox
from cpa_harness.guardrails.sandbox.windows import WindowsSandbox

__all__ = [
    "SandboxResult", "SandboxBackend",
    "PosixSandbox", "InMemorySandbox", "WindowsSandbox",
]
