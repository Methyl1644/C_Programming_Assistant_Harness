"""MockLLM: deterministic LLM for unit tests."""
from cpa_harness.action import Action
from cpa_harness.llm.provider import LLMProvider
from cpa_harness.llm.script import MockTurn


class MockLLM(LLMProvider):
    def __init__(self, script: list[MockTurn]):
        self.script = script
        self.index = 0
        self.call_count = 0

    def chat(self, messages: list, menu: list) -> tuple[str, Action]:
        if self.index >= len(self.script):
            raise IndexError(
                f"MockLLM script exhausted after {self.index} calls; "
                f"add more MockTurn entries"
            )
        turn = self.script[self.index]
        self.index += 1
        self.call_count += 1
        if turn.raise_ is not None:
            raise turn.raise_
        return turn.text, turn.action
