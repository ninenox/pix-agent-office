"""
BaseTool — abstract class สำหรับทุก tool

สร้าง tool ใหม่:
  1. สร้างไฟล์ใน agents/tools/  (เช่น my_tool.py)
  2. สร้าง class ที่ extends BaseTool
  3. กำหนด name, description, input_schema
  4. implement เมธอด run()
  ToolRegistry จะโหลดให้อัตโนมัติเมื่อ restart
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    # ต้องกำหนดใน subclass
    name: str = ""
    description: str = ""
    input_schema: dict = {}

    @abstractmethod
    def run(self, **kwargs) -> str:
        """รัน tool และคืน string result เสมอ (ไม่ raise exception)"""
        ...

    # ─── Schema converters ───

    def to_anthropic_schema(self) -> dict:
        """Schema สำหรับ Anthropic messages.create(tools=[...])"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def to_openai_schema(self) -> dict:
        """Schema สำหรับ OpenAI-compatible chat.completions.create(tools=[...])"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
