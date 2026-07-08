import pytest
from cpa_harness.action import Action
from cpa_harness.llm.mock import MockLLM, MockTurn
from cpa_harness.llm.provider import LLMProvider


def test_mock_llm_returns_scripted_turns():
    mock = MockLLM(script=[
        MockTurn(text="hi", action=Action(type="done")),
        MockTurn(text="bye", action=Action(type="done")),
    ])
    text1, action1 = mock.chat(messages=[], menu=[])
    text2, action2 = mock.chat(messages=[], menu=[])
    assert text1 == "hi"
    assert text2 == "bye"
    assert action1.type == "done"
    assert action2.type == "done"


def test_mock_llm_raises_when_script_exhausted():
    mock = MockLLM(script=[MockTurn(text="x", action=Action(type="done"))])
    mock.chat(messages=[], menu=[])
    with pytest.raises(IndexError):
        mock.chat(messages=[], menu=[])


def test_mock_llm_raises_simulated_error():
    mock = MockLLM(script=[
        MockTurn(text="", action=Action(type="done"), raise_=RuntimeError("LLM down")),
    ])
    with pytest.raises(RuntimeError, match="LLM down"):
        mock.chat(messages=[], menu=[])


def test_mock_llm_satisfies_provider_protocol():
    mock = MockLLM(script=[])
    assert isinstance(mock, LLMProvider)


def test_mock_llm_records_call_count():
    mock = MockLLM(script=[
        MockTurn(text="a", action=Action(type="done")),
        MockTurn(text="b", action=Action(type="done")),
    ])
    assert mock.call_count == 0
    mock.chat([], [])
    assert mock.call_count == 1
    mock.chat([], [])
    assert mock.call_count == 2
