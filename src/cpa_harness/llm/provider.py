"""LLMProvider protocol — abstract interface so tests can swap in MockLLM."""
from typing import Protocol, runtime_checkable
from cpa_harness.action import Action


@runtime_checkable
class LLMProvider(Protocol):
    def chat(self, messages: list, menu: list) -> tuple[str, Action]:
        """Decide what to do this turn. Returns (text, action)."""
        ...
