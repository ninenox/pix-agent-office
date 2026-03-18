"""
Tool: write_file — เขียนไฟล์ไปที่ outputs/
"""

import os
from .base import BaseTool

OUTPUTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
)


class WriteFileTool(BaseTool):
    name = "write_file"
    description = (
        "เขียนหรือบันทึกเนื้อหาเป็นไฟล์ใน outputs/ "
        "ใช้สำหรับบันทึกผลลัพธ์, report, โค้ด หรือข้อมูลที่ต้องการส่งต่อ"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "path ของไฟล์ relative จาก outputs/ เช่น 'report.md' หรือ 'code/solution.py'",
            },
            "content": {
                "type": "string",
                "description": "เนื้อหาที่จะเขียนลงไฟล์",
            },
            "mode": {
                "type": "string",
                "enum": ["write", "append"],
                "description": "'write' = เขียนทับ (default), 'append' = ต่อท้าย",
            },
        },
        "required": ["path", "content"],
    }

    def run(self, path: str, content: str, mode: str = "write", **kwargs) -> str:
        safe = self._safe_path(path)
        if safe is None:
            return "[error] path traversal not allowed"
        try:
            os.makedirs(os.path.dirname(safe), exist_ok=True)
            file_mode = "a" if mode == "append" else "w"
            with open(safe, file_mode, encoding="utf-8") as f:
                f.write(content)
            size = os.path.getsize(safe)
            action = "ต่อท้าย" if mode == "append" else "เขียน"
            return f"✓ {action}ไฟล์ '{path}' สำเร็จ ({size} bytes)"
        except Exception as e:
            return f"[error] เขียนไฟล์ไม่ได้: {e}"

    def _safe_path(self, path: str) -> str | None:
        joined = os.path.abspath(os.path.join(OUTPUTS_DIR, path))
        if not joined.startswith(OUTPUTS_DIR):
            return None
        return joined
