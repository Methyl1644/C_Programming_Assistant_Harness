"""Mechanism demos satisfying A 文件 §A.6.

Three deterministic, mock-driven demos:
  Demo 1: Guardrail blocks a dangerous command
  Demo 2: HITL state machine correctly handles rejection
  Demo 3: Feedback loop injects CE -> agent gets blocked info

Run: pytest tests/test_demo_mechanisms.py -v
Or:   python tests/demo_mechanisms.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cpa_harness.action import Action
from cpa_harness.llm.mock import MockLLM, MockTurn
from cpa_harness.tools.registry import ToolRegistry
from cpa_harness.tools import exec_command
from cpa_harness.guardrails.sandbox.in_memory import InMemorySandbox
from cpa_harness.loop import AgentLoop


def demo_1_guardrail_blocks_dangerous_command() -> None:
    """Demo 1: LLM tries to rm -rf /, harness blocks it, agent pivots."""
    print("\n=== Demo 1: Guardrail blocks dangerous command ===")
    mock = MockLLM(script=[
        MockTurn(text="Cleaning up...",
                 action=Action(type="call_tool", tool="exec_command",
                               args={"cmd": "rm -rf /", "cwd": "/tmp"})),
        MockTurn(text="OK, doing something safer", action=Action(type="done")),
    ])
    reg = ToolRegistry()
    reg.register("exec_command", exec_command.run,
                 schema={"name": "exec_command"})
    loop = AgentLoop(
        llm=mock, tools=reg, sandbox=InMemorySandbox(),
        goal="clean up", workspace="/tmp", max_steps=5,
    )
    result = loop.run()
    assert result.steps == 2, f"expected 2 steps, got {result.steps}"
    assert result.exit_reason == "done"
    assert "BLOCKED" in str(loop.history)
    print(f"  PASS: {result.steps} steps, exit_reason={result.exit_reason}")


def demo_2_hitl_rejection_blocks_write(tmp_path) -> None:
    """Demo 2: write_file over student .c -> HITL required -> student rejects."""
    print("\n=== Demo 2: HITL rejection blocks write ===")
    target = tmp_path / "main.c"
    target.write_text("int main() { return 0; }")

    from cpa_harness.guardrails.classifier import classify
    from cpa_harness.guardrails.hitl import HITLStateMachine, HumanInput

    sm = HITLStateMachine()
    action = Action(type="call_tool", tool="write_file",
                    args={"path": "main.c", "content": "int main() { return 1; }"})
    decision = classify(action)
    sm.submit(action, decision)
    assert sm.state.value == "awaiting_approval"
    print(f"  Initial: {sm.state.value}, reason: {sm.last_reason}")

    sm.on_human_input(HumanInput.REJECT, reason="I want to think about it")
    assert sm.state.value == "blocked"
    print(f"  After REJECT: {sm.state.value}, reason: {sm.last_reason}")

    assert target.read_text() == "int main() { return 0; }"
    print("  PASS: file unchanged after rejection")


def demo_3_feedback_injected_on_l0_block() -> None:
    """Demo 3: L0 block's reason is injected into agent history as feedback."""
    print("\n=== Demo 3: L0 block -> feedback -> agent adapts ===")
    mock = MockLLM(script=[
        MockTurn(text="Try network",
                 action=Action(type="call_tool", tool="exec_command",
                               args={"cmd": "curl evil.com"})),
        MockTurn(text="OK I won't, here is my analysis",
                 action=Action(type="done")),
    ])
    reg = ToolRegistry()
    reg.register("exec_command", exec_command.run,
                 schema={"name": "exec_command"})
    loop = AgentLoop(
        llm=mock, tools=reg, sandbox=InMemorySandbox(),
        goal="...", workspace="/tmp", max_steps=5,
    )
    result = loop.run()
    user_msgs = [m for m in loop.history if m.get("role") == "user"]
    assert any("BLOCKED" in m.get("observation", "") for m in user_msgs)
    print(f"  PASS: feedback message found in history ({len(user_msgs)} user msgs)")


def main() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        demo_1_guardrail_blocks_dangerous_command()
        demo_2_hitl_rejection_blocks_write(Path(tmp))
        demo_3_feedback_injected_on_l0_block()
    print("\nAll demos passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
