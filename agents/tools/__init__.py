"""
ToolRegistry — auto-discovery และจัดการ tools ทั้งหมด

ใช้งาน:
  from tools import registry

  registry.schemas("anthropic")          # schemas ทั้งหมด
  registry.schemas("anthropic", ["read_file", "web_search"])  # เฉพาะบาง tool
  registry.execute("read_file", {"path": "notes.txt"})        # รัน tool
  registry.names()                        # รายชื่อ tools ที่มี
"""

import importlib
import inspect
import os
from .base import BaseTool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def schemas(self, provider: str, names: list[str] = None) -> list[dict]:
        """
        คืน tool schemas ตาม provider

        Args:
            provider: "anthropic" | "openai" | "ollama" (openai-compatible)
            names: รายชื่อ tools ที่ต้องการ — None = ทั้งหมด, ["all"] = ทั้งหมด
        """
        if names is None or names == ["all"]:
            tools = list(self._tools.values())
        else:
            tools = [self._tools[n] for n in names if n in self._tools]

        if provider == "anthropic":
            return [t.to_anthropic_schema() for t in tools]
        else:
            return [t.to_openai_schema() for t in tools]

    def execute(self, name: str, input_data: dict) -> str:
        """รัน tool และคืน string result เสมอ"""
        tool = self._tools.get(name)
        if not tool:
            return f"[error] tool '{name}' not found. available: {self.names()}"
        try:
            return tool.run(**input_data)
        except TypeError as e:
            return f"[error] bad arguments for '{name}': {e}"
        except Exception as e:
            return f"[error] {name} failed: {e}"

    def _autodiscover(self) -> None:
        """โหลด tool classes ทั้งหมดจากไฟล์ใน tools/ อัตโนมัติ"""
        tools_dir = os.path.dirname(__file__)
        for fname in sorted(os.listdir(tools_dir)):
            if fname.startswith("_") or not fname.endswith(".py"):
                continue
            module_name = fname[:-3]
            try:
                module = importlib.import_module(f".{module_name}", package=__package__)
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(cls, BaseTool)
                        and cls is not BaseTool
                        and cls.name  # ต้องมีชื่อ
                    ):
                        self.register(cls())
            except Exception as e:
                print(f"[tools] warning: could not load '{module_name}': {e}")


# Singleton registry — import แล้วใช้ได้เลย
registry = ToolRegistry()
registry._autodiscover()
