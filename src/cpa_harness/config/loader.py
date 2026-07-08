"""Configuration loader: defaults.yaml + optional AGENTS.md override."""
import re
from pathlib import Path
from typing import Any

import yaml


_DEFAULTS_PATH = Path(__file__).parent / "defaults.yaml"
_OVERRIDE_LINE = re.compile(r"^-\s*([a-z_]+):\s*(\S.*)$")


def _parse_agents_md(path: Path) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if not path or not path.exists():
        return overrides
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _OVERRIDE_LINE.match(line.strip())
        if not m:
            continue
        key, raw = m.group(1), m.group(2)
        if raw.lower() in ("true", "false"):
            overrides[key] = raw.lower() == "true"
        else:
            try:
                overrides[key] = int(raw)
            except ValueError:
                overrides[key] = raw
    return overrides


def load_config(agents_md_path: Path | None = None) -> dict[str, Any]:
    defaults = yaml.safe_load(_DEFAULTS_PATH.read_text(encoding="utf-8"))
    if agents_md_path:
        overrides = _parse_agents_md(Path(agents_md_path))
        defaults.update(overrides)
    return defaults
