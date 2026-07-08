"""Tests for config loader — YAML defaults + AGENTS.md override."""
from cpa_harness.config.loader import load_config


def test_load_defaults_only():
    cfg = load_config(agents_md_path=None)
    assert cfg["max_steps"] == 30
    assert cfg["default_model"] == "gpt-4o-mini"


def test_load_overrides_from_agents_md(tmp_path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("""# Project rules
- max_steps: 10
- default_model: deepseek-chat
""")
    cfg = load_config(agents_md_path=agents)
    assert cfg["max_steps"] == 10
    assert cfg["default_model"] == "deepseek-chat"
    assert cfg["max_tokens"] == 8000


def test_agents_md_with_no_overrides_keeps_defaults(tmp_path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# just a header\n")
    cfg = load_config(agents_md_path=agents)
    assert cfg["max_steps"] == 30
