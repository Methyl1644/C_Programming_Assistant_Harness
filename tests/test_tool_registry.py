"""Tests for ToolRegistry and individual tool implementations."""
import pytest
from cpa_harness.tools.registry import ToolRegistry
from cpa_harness.tools import read_file, list_dir, search_code


def test_registry_register_and_list():
    reg = ToolRegistry()
    reg.register("read_file", read_file.run, schema={"name": "read_file"})
    assert "read_file" in reg.names()


def test_registry_dispatch_read_file(tmp_path):
    (tmp_path / "main.c").write_text("int main() { return 0; }")
    reg = ToolRegistry()
    reg.register("read_file", read_file.run, schema={"name": "read_file"})
    obs = reg.dispatch("read_file", {"path": "main.c"}, sandbox=None, cwd=str(tmp_path))
    assert "int main" in obs.result


def test_registry_unknown_tool_raises():
    reg = ToolRegistry()
    with pytest.raises(KeyError):
        reg.dispatch("nope", {}, sandbox=None, cwd="/tmp")


def test_read_file_tool(tmp_path):
    (tmp_path / "x.txt").write_text("hello")
    from cpa_harness.tools.read_file import run
    obs = run({"path": "x.txt"}, cwd=str(tmp_path))
    assert obs.result == "hello"


def test_list_dir_tool(tmp_path):
    (tmp_path / "a.c").write_text("")
    (tmp_path / "b.h").write_text("")
    from cpa_harness.tools.list_dir import run
    obs = run({"path": "."}, cwd=str(tmp_path))
    assert "a.c" in obs.result
    assert "b.h" in obs.result


def test_search_code_tool(tmp_path):
    (tmp_path / "main.c").write_text("int x = 0;\nint y = malloc(4);")
    from cpa_harness.tools.search_code import run
    obs = run({"pattern": "malloc", "path": "."}, cwd=str(tmp_path))
    assert "malloc" in obs.result
