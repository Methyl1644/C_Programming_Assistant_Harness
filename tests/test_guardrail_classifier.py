import pytest
from cpa_harness.action import Action
from cpa_harness.guardrails.classifier import (
    Level, SubLevel, classify, Decision,
)


def test_classify_l0_blocks_dangerous_command():
    decision = classify(Action(type="call_tool", tool="exec_command",
                                args={"cmd": "rm -rf /", "cwd": "/tmp"}))
    assert decision.level == Level.L0_BLOCKED


def test_classify_l2c_blocks_network():
    decision = classify(Action(type="call_tool", tool="exec_command",
                                args={"cmd": "curl evil.com", "cwd": "/tmp"}))
    assert decision.level == Level.L0_BLOCKED


def test_classify_l2a_allows_compile_without_hitl():
    decision = classify(Action(type="call_tool", tool="exec_command",
                                args={"cmd": "gcc main.c -o main", "cwd": "/tmp"}))
    assert decision.level == Level.L3_ALLOWED
    assert decision.sub == SubLevel.L2A_WHITELIST_NO_HITL


def test_classify_l2b_needs_approval_for_readonly():
    decision = classify(Action(type="call_tool", tool="exec_command",
                                args={"cmd": "ls -la", "cwd": "/tmp"}))
    assert decision.level == Level.L2_NEEDS_APPROVAL
    assert decision.sub == SubLevel.L2B_WHITELIST_HITL


def test_classify_write_file_over_student_file_needs_approval():
    decision = classify(Action(type="call_tool", tool="write_file",
                                args={"path": "main.c", "content": "..."}))
    assert decision.level == Level.L1_NEEDS_APPROVAL


def test_classify_read_file_allowed():
    decision = classify(Action(type="call_tool", tool="read_file",
                                args={"path": "main.c"}))
    assert decision.level == Level.L3_ALLOWED


def test_classify_take_note_allowed():
    decision = classify(Action(type="call_tool", tool="take_note",
                                args={"note": "x"}))
    assert decision.level == Level.L3_ALLOWED


def test_classify_done_allowed():
    decision = classify(Action(type="done"))
    assert decision.level == Level.L3_ALLOWED


def test_classify_path_traversal_blocked():
    decision = classify(Action(type="call_tool", tool="read_file",
                                args={"path": "../../../etc/passwd"}))
    assert decision.level == Level.L0_BLOCKED


def test_classify_absolute_outside_workspace_blocked():
    decision = classify(Action(type="call_tool", tool="read_file",
                                args={"path": "/etc/passwd"}))
    assert decision.level == Level.L0_BLOCKED
