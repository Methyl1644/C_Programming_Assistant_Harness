"""CLI entry point. Subcommands: run / setup / key."""
import argparse
import sys
from pathlib import Path

from cpa_harness.action import Action
from cpa_harness.llm.mock import MockLLM, MockTurn
from cpa_harness.llm.openai_provider import OpenAILLM
from cpa_harness.tools.registry import ToolRegistry
from cpa_harness.tools import read_file, list_dir, search_code, write_file, exec_command, take_note, finish_tutoring, run_feedback
from cpa_harness.guardrails.sandbox.in_memory import InMemorySandbox
from cpa_harness.guardrails.sandbox.posix import PosixSandbox
from cpa_harness.guardrails.sandbox.windows import WindowsSandbox
from cpa_harness.loop import AgentLoop
from cpa_harness.config import load_config
from cpa_harness.credentials import get_api_key


def _build_sandbox(workspace: str):
    if sys.platform == "win32":
        try:
            return WindowsSandbox(workspace=workspace)
        except Exception:
            return InMemorySandbox()
    try:
        return PosixSandbox(workspace=workspace)
    except Exception:
        return InMemorySandbox()


def _build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    def schema(name):
        return {"name": name, "description": name, "parameters": {"type": "object"}}
    for mod, name in [
        (read_file, "read_file"),
        (list_dir, "list_dir"),
        (search_code, "search_code"),
        (write_file, "write_file"),
        (exec_command, "exec_command"),
        (take_note, "take_note"),
        (finish_tutoring, "finish_tutoring"),
        (run_feedback, "run_feedback"),
    ]:
        reg.register(name, mod.run, schema(name))
    return reg


def cmd_run(args) -> int:
    cfg = load_config()
    workspace = str(Path(args.file).parent)
    if args.mock:
        llm = MockLLM(script=[
            MockTurn(text=f"I will read {args.file}",
                     action=Action(type="call_tool", tool="read_file",
                                   args={"path": Path(args.file).name})),
            MockTurn(text="Done", action=Action(type="done")),
        ])
    else:
        llm = OpenAILLM(api_key=get_api_key(), model=cfg["default_model"])
    loop = AgentLoop(
        llm=llm,
        tools=_build_registry(),
        sandbox=_build_sandbox(workspace),
        goal=args.goal,
        workspace=workspace,
        max_steps=cfg["max_steps"],
    )
    result = loop.run()
    print(f"Result: {result.answer}")
    print(f"Steps: {result.steps}, exit: {result.exit_reason}")
    return 0 if result.exit_reason == "done" else 1


def cmd_setup(args) -> int:
    from cpa_harness.credentials.setup import run_setup
    run_setup()
    return 0


def cmd_key(args) -> int:
    from cpa_harness.credentials.status import print_status
    print_status()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="cpa-harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="Run harness on a file")
    pr.add_argument("--file", required=True)
    pr.add_argument("--goal", required=True)
    pr.add_argument("--mock", action="store_true", help="use MockLLM (no API key)")
    pr.set_defaults(func=cmd_run)

    sub.add_parser("setup", help="Configure API key").set_defaults(func=cmd_setup)
    sub.add_parser("key", help="Show API key status").set_defaults(func=cmd_key)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
