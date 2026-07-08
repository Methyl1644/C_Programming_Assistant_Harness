"""OpenAI-compatible LLM provider.

Works with OpenAI, DeepSeek, 硅基流动, etc.
"""
import json
import os

from cpa_harness.action import Action
from cpa_harness.llm.provider import LLMProvider


class OpenAILLM(LLMProvider):
    def __init__(self, api_key: str | None = None,
                 base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url
        self.model = model
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def chat(self, messages: list, menu: list) -> tuple[str, Action]:
        client = self._ensure_client()
        kwargs = {"model": self.model, "messages": messages}
        if menu:
            kwargs["tools"] = [{"type": "function", "function": s} for s in menu]
            kwargs["tool_choice"] = "auto"
        resp = client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        text = msg.content or ""
        if msg.tool_calls:
            tc = msg.tool_calls[0]
            args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            return text, Action(type="call_tool", tool=tc.function.name, args=args)
        return text, Action(type="done")
