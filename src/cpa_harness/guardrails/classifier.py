"""ActionClassifier: deterministic dangerous-action classification.

This is the entry point of the governance pipeline. The harness
calls `classify(action)` on every action before sandbox execution.
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath

from cpa_harness.action import Action
from cpa_harness.guardrails.patterns import (
    L0_PATTERNS, L2A_WHITELIST, L2B_WHITELIST, L2C_BLACKLIST, matches_any,
)


class Level(str, Enum):
    L0_BLOCKED = "L0"
    L1_NEEDS_APPROVAL = "L1"
    L2_NEEDS_APPROVAL = "L2"
    L3_ALLOWED = "L3"


class SubLevel(str, Enum):
    L2A_WHITELIST_NO_HITL = "L2a"
    L2B_WHITELIST_HITL = "L2b"
    L2C_BLACKLIST = "L2c"
    NONE = ""


@dataclass
class Decision:
    level: Level
    sub: SubLevel = SubLevel.NONE
    reason: str = ""


_STUDENT_FILE_EXTENSIONS = {".c", ".h"}


def _first_token(cmd: str) -> str:
    return cmd.strip().split()[0] if cmd.strip() else ""


def _is_path_safe(path: str) -> bool:
    """Refuse any path that escapes the workspace or is absolute outside it."""
    if not path:
        return False
    p = PurePosixPath(path)
    if p.is_absolute():
        return False
    if ".." in p.parts:
        return False
    return True


def classify(action: Action) -> Decision:
    if action.type in ("done", "take_note", "use_skill", "finish_tutoring"):
        return Decision(Level.L3_ALLOWED, reason=f"action type {action.type} always allowed")

    if action.type != "call_tool":
        return Decision(Level.L0_BLOCKED, reason=f"unknown action type: {action.type}")

    tool = action.tool
    args = action.args or {}

    if tool in ("read_file", "list_dir", "search_code", "run_feedback",
                 "take_note", "finish_tutoring"):
        if tool in ("read_file", "list_dir", "search_code", "run_feedback"):
            path = args.get("path") or args.get("target") or ""
            if not _is_path_safe(path):
                return Decision(Level.L0_BLOCKED, reason=f"unsafe path: {path!r}")
        return Decision(Level.L3_ALLOWED, reason=f"safe tool {tool}")

    if tool == "write_file":
        path = args.get("path", "")
        if not _is_path_safe(path):
            return Decision(Level.L0_BLOCKED, reason=f"unsafe write path: {path!r}")
        ext = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        if ext in _STUDENT_FILE_EXTENSIONS:
            return Decision(Level.L1_NEEDS_APPROVAL, reason=f"overwrites student file {path!r}")
        return Decision(Level.L1_NEEDS_APPROVAL, reason="write requires HITL")

    if tool == "exec_command":
        cmd = args.get("cmd", "")
        if matches_any(cmd, L0_PATTERNS):
            return Decision(Level.L0_BLOCKED, sub=SubLevel.L2C_BLACKLIST,
                            reason=f"L0 pattern matched in {cmd!r}")
        first = _first_token(cmd)
        if first in L2C_BLACKLIST:
            return Decision(Level.L0_BLOCKED, sub=SubLevel.L2C_BLACKLIST,
                            reason=f"blacklisted command: {first}")
        if first in L2A_WHITELIST:
            return Decision(Level.L3_ALLOWED, sub=SubLevel.L2A_WHITELIST_NO_HITL,
                            reason=f"whitelisted compile tool: {first}")
        if first in L2B_WHITELIST:
            return Decision(Level.L2_NEEDS_APPROVAL, sub=SubLevel.L2B_WHITELIST_HITL,
                            reason=f"readonly tool {first} needs HITL")
        return Decision(Level.L2_NEEDS_APPROVAL,
                        reason=f"unknown command {first!r} needs HITL")

    return Decision(Level.L0_BLOCKED, reason=f"unknown tool: {tool!r}")
