"""MockTurn: one pre-programmed step in a MockLLM script."""
from dataclasses import dataclass
from cpa_harness.action import Action


@dataclass
class MockTurn:
    text: str
    action: Action
    raise_: Exception | None = None
