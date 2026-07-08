"""Tests for OpenAI-compatible LLM provider."""
import json
from cpa_harness.llm.openai_provider import OpenAILLM
from cpa_harness.llm.provider import LLMProvider


def test_openai_llm_satisfies_provider_protocol():
    llm = OpenAILLM(api_key="sk-test", base_url="https://api.openai.com/v1",
                    model="gpt-4o-mini")
    assert isinstance(llm, LLMProvider)


def test_openai_llm_chat_returns_text_and_action():
    class FakeChoice:
        def __init__(self, message): self.message = message
    class FakeMessage:
        def __init__(self, content, tool_calls): self.content = content; self.tool_calls = tool_calls
    class FakeToolCall:
        def __init__(self, function): self.function = function
    class FakeFunction:
        def __init__(self, name, arguments): self.name = name; self.arguments = arguments
    class FakeResponse:
        def __init__(self, choices): self.choices = choices

    fake_response = FakeResponse(choices=[
        FakeChoice(FakeMessage(
            content="Let me read it",
            tool_calls=[FakeToolCall(FakeFunction(
                name="read_file",
                arguments=json.dumps({"path": "main.c"}),
            ))],
        )),
    ])

    llm = OpenAILLM(api_key="sk-test", base_url="https://x", model="gpt-4o-mini")
    llm._client = type("FakeClient", (), {
        "chat": type("FakeCompletions", (), {
            "completions": type("FakeCreate", (), {
                "create": lambda **kwargs: fake_response,
            })(),
        })(),
    })()

    text, action = llm.chat(messages=[{"role": "user", "content": "hi"}], menu=[])
    assert text == "Let me read it"
    assert action.type == "call_tool"
    assert action.tool == "read_file"
    assert action.args == {"path": "main.c"}
