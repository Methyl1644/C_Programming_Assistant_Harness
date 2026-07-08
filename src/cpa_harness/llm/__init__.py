"""LLM abstraction layer."""
from cpa_harness.llm.provider import LLMProvider
from cpa_harness.llm.mock import MockLLM
from cpa_harness.llm.script import MockTurn

__all__ = ["LLMProvider", "MockLLM", "MockTurn"]
