"""Static pattern tables for dangerous-command classification."""
import re

# L0: always block, no HITL. Match anywhere in the command.
L0_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\brm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r)\b.*\/", re.IGNORECASE),
    re.compile(r"\brm\s+-rf\s*\/\s*$", re.IGNORECASE),
    re.compile(r"\bmkfs\b", re.IGNORECASE),
    re.compile(r"\bshutdown\b", re.IGNORECASE),
    re.compile(r"\breboot\b", re.IGNORECASE),
    re.compile(r"\bdd\s+.*\bof=/dev/", re.IGNORECASE),
    re.compile(r":\(\)\s*\{.*:\|\:&\s*\}\s*;\s*:"),  # fork bomb
]

# L2a: whitelist, no HITL needed (compile/test tools)
L2A_WHITELIST: set[str] = {
    "gcc", "cc", "g++", "clang", "make", "cmake",
    "valgrind", "cppcheck", "gdb",
    "timeout",
}

# L2b: whitelist, but HITL still required (read-only tools)
L2B_WHITELIST: set[str] = {
    "ls", "cat", "head", "tail", "wc", "file", "stat", "pwd", "echo",
    "grep", "find", "tree",
}

# L2c: blacklist, always block (network / shell trickery)
L2C_BLACKLIST: set[str] = {
    "curl", "wget", "nc", "netcat", "ssh", "scp", "rsync",
    "python3", "python", "perl", "ruby", "node",
    "bash", "sh", "zsh", "fish",
}


def matches_any(text: str, patterns: list[re.Pattern[str]]) -> bool:
    """Return True if any pattern matches anywhere in text."""
    return any(p.search(text) for p in patterns)
