"""HITL state machine. Implements SPEC §5.3 state diagram."""
from enum import Enum
from cpa_harness.action import Action
from cpa_harness.guardrails.classifier import Decision, Level


class State(str, Enum):
    IDLE = "idle"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    BLOCKED = "blocked"
    FAILED = "failed"


class HumanInput(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"


class ApprovalRequired(Exception):
    """Raised when human input arrives but no action is awaiting approval."""


class HITLStateMachine:
    def __init__(self):
        self.state = State.IDLE
        self.pending_action: Action | None = None
        self.last_reason = ""

    def submit(self, action: Action, decision: Decision) -> None:
        self.pending_action = action
        self.last_reason = decision.reason

        if decision.level == Level.L0_BLOCKED:
            self.state = State.BLOCKED
        elif decision.level in (Level.L1_NEEDS_APPROVAL, Level.L2_NEEDS_APPROVAL):
            self.state = State.AWAITING_APPROVAL
        elif decision.level == Level.L3_ALLOWED:
            self.state = State.RUNNING
        else:
            self.state = State.FAILED

    def on_human_input(self, input_: HumanInput, *,
                       new_action: Action | None = None,
                       reason: str = "") -> None:
        if self.state != State.AWAITING_APPROVAL:
            raise ApprovalRequired(
                f"Cannot apply {input_.value} in state {self.state.value}"
            )
        if input_ == HumanInput.APPROVE:
            self.state = State.RUNNING
            self.pending_action = None
        elif input_ == HumanInput.REJECT:
            self.state = State.BLOCKED
            self.last_reason = reason or "rejected by user"
            self.pending_action = None
        elif input_ == HumanInput.EDIT:
            if new_action is None:
                raise ValueError("EDIT requires new_action")
            self.pending_action = new_action
