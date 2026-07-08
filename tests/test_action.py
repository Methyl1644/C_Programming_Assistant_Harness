import pytest
from cpa_harness.action import Action


def test_action_call_tool():
    a = Action(type="call_tool", tool="read_file", args={"path": "main.c"})
    assert a.type == "call_tool"
    assert a.tool == "read_file"
    assert a.args == {"path": "main.c"}


def test_action_take_note():
    a = Action(type="take_note", note="student is on pointer chapter")
    assert a.type == "take_note"
    assert a.note == "student is on pointer chapter"


def test_action_finish_tutoring():
    a = Action(type="finish_tutoring", summary="done")
    assert a.type == "finish_tutoring"


def test_action_done():
    a = Action(type="done")
    assert a.type == "done"


def test_action_use_skill():
    a = Action(type="use_skill", tool="test-driven-development")
    assert a.type == "use_skill"


def test_action_invalid_type_raises():
    with pytest.raises(ValueError):
        Action(type="fly_to_mars")
