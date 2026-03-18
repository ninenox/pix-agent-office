"""
Tests for agents/tools/
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))

from tools.read_file import ReadFileTool
from tools.write_file import WriteFileTool
from tools.run_python import RunPythonTool
from tools.shell_command import ShellCommandTool
from tools import registry


# ─── ReadFileTool ───

class TestReadFileTool:
    def setup_method(self):
        self.tool = ReadFileTool()

    def test_path_traversal_blocked(self):
        result = self.tool.run("../../etc/passwd")
        assert "[error]" in result
        assert "path traversal" in result

    def test_file_not_found(self):
        result = self.tool.run("nonexistent_file_xyz.txt")
        assert "[error]" in result

    def test_schema_has_required_fields(self):
        schema = self.tool.to_anthropic_schema()
        assert schema["name"] == "read_file"
        assert "description" in schema
        assert "input_schema" in schema


# ─── WriteFileTool ───

class TestWriteFileTool:
    def setup_method(self):
        self.tool = WriteFileTool()

    def test_path_traversal_blocked(self):
        result = self.tool.run("../../etc/evil.txt", "hacked")
        assert "[error]" in result
        assert "path traversal" in result

    def test_write_and_read_back(self, tmp_path, monkeypatch):
        import tools.write_file as wf
        monkeypatch.setattr(wf, "OUTPUTS_DIR", str(tmp_path))
        self.tool = WriteFileTool()
        result = self.tool.run("hello.txt", "สวัสดี")
        assert "[error]" not in result
        assert os.path.exists(tmp_path / "hello.txt")
        assert (tmp_path / "hello.txt").read_text(encoding="utf-8") == "สวัสดี"

    def test_append_mode(self, tmp_path, monkeypatch):
        import tools.write_file as wf
        monkeypatch.setattr(wf, "OUTPUTS_DIR", str(tmp_path))
        self.tool = WriteFileTool()
        self.tool.run("log.txt", "line1\n")
        self.tool.run("log.txt", "line2\n", mode="append")
        content = (tmp_path / "log.txt").read_text(encoding="utf-8")
        assert "line1" in content
        assert "line2" in content


# ─── RunPythonTool ───

class TestRunPythonTool:
    def setup_method(self):
        self.tool = RunPythonTool()

    def test_basic_print(self):
        result = self.tool.run("print('hello')")
        assert result == "hello"

    def test_calculation(self):
        result = self.tool.run("print(2 + 2)")
        assert result == "4"

    def test_syntax_error(self):
        result = self.tool.run("def broken(")
        assert "[exit" in result or "[error]" in result

    def test_timeout(self):
        result = self.tool.run("import time; time.sleep(20)")
        assert "timeout" in result

    def test_thai_output(self):
        result = self.tool.run("print('สวัสดี')")
        assert "สวัสดี" in result

    def test_no_output(self):
        result = self.tool.run("x = 1 + 1")
        assert "รันสำเร็จ" in result


# ─── ShellCommandTool ───

class TestShellCommandTool:
    def setup_method(self):
        self.tool = ShellCommandTool()

    def test_basic_command(self):
        result = self.tool.run("echo hello")
        assert "hello" in result

    def test_blocked_rm(self):
        result = self.tool.run("rm -rf /tmp/test")
        assert "[error]" in result

    def test_blocked_sudo(self):
        result = self.tool.run("sudo ls")
        assert "[error]" in result

    def test_blocked_curl(self):
        result = self.tool.run("curl http://example.com")
        assert "[error]" in result

    def test_ls_command(self):
        result = self.tool.run("ls /tmp")
        assert "[error]" not in result


# ─── ToolRegistry ───

class TestToolRegistry:
    def test_registry_has_tools(self):
        names = registry.names()
        assert len(names) > 0

    def test_expected_tools_loaded(self):
        names = registry.names()
        for expected in ["read_file", "write_file", "run_python", "shell_command"]:
            assert expected in names, f"tool '{expected}' not found in registry"

    def test_execute_unknown_tool(self):
        result = registry.execute("nonexistent_tool", {})
        assert "[error]" in result

    def test_schemas_anthropic(self):
        schemas = registry.schemas("anthropic", ["read_file"])
        assert len(schemas) == 1
        assert schemas[0]["name"] == "read_file"
        assert "input_schema" in schemas[0]

    def test_schemas_openai(self):
        schemas = registry.schemas("openai", ["run_python"])
        assert len(schemas) == 1
        assert schemas[0]["type"] == "function"
        assert schemas[0]["function"]["name"] == "run_python"

    def test_schemas_all(self):
        all_schemas = registry.schemas("openai", ["all"])
        named_schemas = registry.schemas("openai", registry.names())
        assert len(all_schemas) == len(named_schemas)
