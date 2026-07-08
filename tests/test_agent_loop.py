"""Tests for AgentLoop — the main agent loop integrating LLM + classifier + HITL + tools."""
import pytest
from cpa_harness.action import Action
from cpa_harness.llm.mock import MockLLM, MockTurn
from cpa_harness.tools.registry import ToolRegistry
from cpa_harness.guardrails.sandbox.in_memory import InMemorySandbox
from cpa_harness.loop import AgentLoop, LoopResult


def test_loop_exits_on_done_action():
    mock = MockLLM(script=[MockTurn(text="All done", action=Action(type="done"))])
    loop = AgentLoop(
        llm=mock, tools=ToolRegistry(), sandbox=InMemorySandbox(),
        goal="say hi", workspace="/tmp", max_steps=5,
    )
    result = loop.run()
    assert isinstance(result, LoopResult)
    assert result.answer == "All done"
    assert result.steps == 1
    assert result.exit_reason == "done"


def test_loop_calls_read_file_then_done(tmp_path):
    (tmp_path / "main.c").write_text("int main() {}")
    mock = MockLLM(script=[
        MockTurn(text="I'll read it",
                 action=Action(type="call_tool", tool="read_file",
                               args={"path": "main.c"})),
        MockTurn(text="got it", action=Action(type="done")),
    ])
    reg = ToolRegistry()
    from cpa_harness.tools.read_file import run as read_run
    reg.register("read_file", read_run, schema={"name": "read_file"})
    loop = AgentLoop(
        llm=mock, tools=reg, sandbox=InMemorySandbox(),
        goal="read main.c", workspace=str(tmp_path), max_steps=5,
    )
    result = loop.run()
    assert result.exit_reason == "done"
    assert result.steps == 2


def test_loop_blocks_dangerous_command():
    mock = MockLLM(script=[
        MockTurn(text="I'll clean up",
                 action=Action(type="call_tool", tool="exec_command",
                               args={"cmd": "rm -rf /", "cwd": "/tmp"})),
        MockTurn(text="OK I'll do something else", action=Action(type="done")),
    ])
    reg = ToolRegistry()
    from cpa_harness.tools.exec_command import run as exec_run
    reg.register("exec_command", exec_run, schema={"name": "exec_command"})
    loop = AgentLoop(
        llm=mock, tools=reg, sandbox=InMemorySandbox(),
        goal="clean up", workspace="/tmp", max_steps=5,
    )
    result = loop.run()
    assert result.steps == 2
    assert result.exit_reason == "done"


def test_loop_max_steps_terminates():
    mock = MockLLM(script=[
        MockTurn(text="thinking", action=Action(type="take_note", note="x"))
        for _ in range(10)
    ])
    reg = ToolRegistry()
    from cpa_harness.tools.take_note import run as note_run
    reg.register("take_note", note_run, schema={"name": "take_note"})
    loop = AgentLoop(
        llm=mock, tools=reg, sandbox=InMemorySandbox(),
        goal="loop forever", workspace="/tmp", max_steps=3,
    )
    result = loop.run()
    assert result.steps == 3
    assert result.exit_reason == "max_steps"
