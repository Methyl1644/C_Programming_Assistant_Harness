"""ToolRegistry: central place to register and dispatch tools."""
from typing import Callable
from cpa_harness.observation import Observation
from cpa_harness.guardrails.sandbox.backend import SandboxBackend


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._schemas: dict[str, dict] = {}

    def register(self, name: str, fn: Callable, schema: dict) -> None:
        self._tools[name] = fn
        self._schemas[name] = schema

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def schemas(self) -> list[dict]:
        return list(self._schemas.values())

    def dispatch(self, name: str, args: dict, *, sandbox: SandboxBackend | None, cwd: str) -> Observation:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name!r}")
        fn = self._tools[name]
        try:
            return fn(args, cwd=cwd, sandbox=sandbox)
        except TypeError:
            return fn(args, cwd=cwd)
