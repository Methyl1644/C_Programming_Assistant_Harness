"""Tests for valgrind output parser (MLE feedback signal)."""
from cpa_harness.feedback.valgrind_parser import parse_valgrind


def test_parse_leak_summary():
    stderr = """
==12345== HEAP SUMMARY:
==12345==   in use at exit: 40 bytes in 1 blocks
==12345== LEAK SUMMARY:
==12345==   definitely lost: 40 bytes in 1 blocks
"""
    report = parse_valgrind(stderr)
    assert report is not None
    assert report.verdict == "MLE"
    assert "40 bytes" in report.leak_summary


def test_parse_no_leak_returns_none():
    stderr = """
==12345== HEAP SUMMARY:
==12345==   in use at exit: 0 bytes in 0 blocks
==12345== LEAK SUMMARY:
==12345==   definitely lost: 0 bytes in 0 blocks
"""
    assert parse_valgrind(stderr) is None


def test_parse_invalid_read():
    stderr = """
==12345== Invalid read of size 4
==12345==    at 0x401234: main (main.c:5)
==12345== LEAK SUMMARY:
==12345==   definitely lost: 0 bytes in 0 blocks
"""
    report = parse_valgrind(stderr)
    assert report is not None
    assert "Invalid read" in report.msg
    assert report.line == 5
