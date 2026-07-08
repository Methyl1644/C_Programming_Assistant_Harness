"""exec_command tool. Routes through the provided sandbox."""
from cpa_harness.observation import Observation
from cpa_harness.guardrails.sandbox.backend import SandboxBackend


def run(args: dict, cwd: str, sandbox: SandboxBackend) -> Observation:
    result = sandbox.run("exec_command", {"cmd": args["cmd"]}, cwd=cwd)
    return Observation.from_sandbox_result(result, tool="exec_command")
