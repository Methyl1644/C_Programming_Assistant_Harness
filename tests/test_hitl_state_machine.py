import pytest
from cpa_harness.action import Action
from cpa_harness.guardrails.classifier import Decision, Level, SubLevel
from cpa_harness.guardrails.hitl import (
    HITLStateMachine, State, HumanInput, ApprovalRequired,
)


def _approval_decision():
    return Decision(Level.L1_NEEDS_APPROVAL, reason="overwrites student file")


def test_initial_state_is_idle():
    sm = HITLStateMachine()
    assert sm.state == State.IDLE


def test_l0_action_is_blocked_immediately():
    sm = HITLStateMachine()
    action = Action(type="call_tool", tool="exec_command",
                    args={"cmd": "rm -rf /", "cwd": "/tmp"})
    sm.submit(action, Decision(Level.L0_BLOCKED, reason="L0 pattern"))
    assert sm.state == State.BLOCKED


def test_l3_action_runs_immediately():
    sm = HITLStateMachine()
    action = Action(type="call_tool", tool="read_file", args={"path": "main.c"})
    sm.submit(action, Decision(Level.L3_ALLOWED))
    assert sm.state == State.RUNNING


def test_l1_action_awaits_approval():
    sm = HITLStateMachine()
    action = Action(type="call_tool", tool="write_file",
                    args={"path": "main.c", "content": "..."})
    sm.submit(action, _approval_decision())
    assert sm.state == State.AWAITING_APPROVAL
    assert sm.pending_action is action


def test_approval_transitions_to_running():
    sm = HITLStateMachine()
    sm.submit(Action(type="call_tool", tool="write_file",
                     args={"path": "main.c", "content": "x"}),
              _approval_decision())
    sm.on_human_input(HumanInput.APPROVE)
    assert sm.state == State.RUNNING
    assert sm.pending_action is None


def test_rejection_transitions_to_blocked():
    sm = HITLStateMachine()
    sm.submit(Action(type="call_tool", tool="write_file",
                     args={"path": "main.c", "content": "x"}),
              _approval_decision())
    sm.on_human_input(HumanInput.REJECT, reason="not now")
    assert sm.state == State.BLOCKED
    assert "not now" in sm.last_reason


def test_edit_returns_to_awaiting_with_modified_action():
    sm = HITLStateMachine()
    action = Action(type="call_tool", tool="write_file",
                    args={"path": "main.c", "content": "original"})
    sm.submit(action, _approval_decision())
    edited = Action(type="call_tool", tool="write_file",
                    args={"path": "main.c", "content": "edited"})
    sm.on_human_input(HumanInput.EDIT, new_action=edited)
    assert sm.state == State.AWAITING_APPROVAL
    assert sm.pending_action.args["content"] == "edited"


def test_cannot_input_when_not_awaiting():
    sm = HITLStateMachine()
    with pytest.raises(ApprovalRequired):
        sm.on_human_input(HumanInput.APPROVE)
