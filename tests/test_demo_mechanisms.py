"""Run the mechanism demos as pytest tests so CI verifies them."""
import tempfile
from pathlib import Path

from tests.demo_mechanisms import (
    demo_1_guardrail_blocks_dangerous_command,
    demo_2_hitl_rejection_blocks_write,
    demo_3_feedback_injected_on_l0_block,
)


def test_demo_1():
    demo_1_guardrail_blocks_dangerous_command()


def test_demo_2():
    with tempfile.TemporaryDirectory() as tmp:
        demo_2_hitl_rejection_blocks_write(Path(tmp))


def test_demo_3():
    demo_3_feedback_injected_on_l0_block()
