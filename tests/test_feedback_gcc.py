"""Tests for gcc error parser (CE feedback signal)."""
from cpa_harness.feedback.gcc_parser import parse_gcc


def test_parse_simple_error():
    stderr = "main.c:5:12: error: 'x' undeclared (first use in this function)"
    report = parse_gcc(stderr, file="main.c")
    assert report is not None
    assert report.verdict == "CE"
    assert report.line == 5
    assert report.col == 12
    assert "undeclared" in report.msg


def test_parse_warning():
    stderr = "main.c:3:1: warning: unused variable 'y'"
    report = parse_gcc(stderr, file="main.c")
    assert report is not None
    assert report.severity == "warning"


def test_parse_multiple_errors_returns_first():
    stderr = (
        "main.c:5:1: error: 'a' undeclared\n"
        "main.c:10:1: error: 'b' undeclared\n"
    )
    report = parse_gcc(stderr, file="main.c")
    assert report.line == 5


def test_parse_no_error_returns_none():
    assert parse_gcc("", file="main.c") is None
    assert parse_gcc("main.c:3:1: note: previous definition", file="main.c") is None
