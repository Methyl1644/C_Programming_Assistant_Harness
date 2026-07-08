"""AgentLoop: the main agent loop (per SPEC §6.2)."""
from dataclasses import dataclass

from cpa_harness.action import Action
from cpa_harness.guardrails.classifier import classify
from cpa_harness.guardrails.hitl import HITLStateMachine, State, HumanInput
from cpa_harness.guardrails.sandbox.backend import SandboxBackend
from cpa_harness.llm.provider import LLMProvider
from cpa_harness.observation import Observation
from cpa_harness.tools.registry import ToolRegistry


@dataclass
class LoopResult:
    answer: str
    steps: int
    exit_reason: str  # "done" | "max_steps" | "awaiting_human"


class AgentLoop:
    def __init__(
        self,
        *,
        llm: LLMProvider,
        tools: ToolRegistry,
        sandbox: SandboxBackend,
        goal: str,
        workspace: str,
        max_steps: int = 30,
        auto_approve: bool = True,
    ):
        self.llm = llm
        self.tools = tools
        self.sandbox = sandbox
        self.goal = goal
        self.workspace = workspace
        self.max_steps = max_steps
        self.auto_approve = auto_approve
        self.history: list[dict] = []
        self.hitl = HITLStateMachine()

    def run(self) -> LoopResult:
        answer = ""
        for step in range(1, self.max_steps + 1):
            text, action = self.llm.chat(messages=self.history, menu=self.tools.schemas())
            self.history.append({"role": "assistant", "text": text, "action": action.model_dump()})

            if action.type == "done":
                return LoopResult(answer=text, steps=step, exit_reason="done")
            if action.type == "finish_tutoring":
                return LoopResult(answer=action.summary or text, steps=step, exit_reason="done")

            decision = classify(action)
            self.hitl.submit(action, decision)

            if self.hitl.state == State.BLOCKED:
                obs = Observation(
                    tool=action.tool or "unknown",
                    result=f"BLOCKED ({decision.reason})",
                    exit_code=1,
                )
                self.history.append({"role": "user", "observation": obs.result})
                continue

            if self.hitl.state == State.AWAITING_APPROVAL:
                if self.auto_approve:
                    self.hitl.on_human_input(HumanInput.APPROVE)
                else:
                    return LoopResult(answer="", steps=step, exit_reason="awaiting_human")

            try:
                obs = self.tools.dispatch(
                    action.tool, action.args,
                    sandbox=self.sandbox, cwd=self.workspace,
                )
            except Exception as e:
                obs = Observation(tool=action.tool or "?", result=f"ERROR: {e}", exit_code=1)
            self.history.append({"role": "user", "observation": obs.result})
        return LoopResult(answer=answer, steps=self.max_steps, exit_reason="max_steps")
