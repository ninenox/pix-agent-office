"""
Tool: read_file — อ่านไฟล์จาก workspace/
"""

import os
from .base import BaseTool

WORKSPACE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "workspace")
)


class ReadFileTool(BaseTool):
    name = "read_file"
    description = (
        "อ่านเนื้อหาไฟล์จาก workspace/ "
        "ใช้สำหรับอ่าน notes, input data หรือไฟล์ที่ agent อื่นเขียนไว้"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "path ของไฟล์ relative จาก workspace/ เช่น 'notes.txt' หรือ 'data/input.json'",
            },
        },
        "required": ["path"],
    }

    def run(self, path: str, **kwargs) -> str:
        safe = self._safe_path(path)
        if safe is None:
            return "[error] path traversal not allowed"
        if not os.path.exists(safe):
            available = self._list_files()
            hint = f"ไฟล์ที่มีใน workspace: {available}" if available else "workspace ว่างเปล่า"
            return f"[error] ไม่พบไฟล์ '{path}'. {hint}"
        try:
            with open(safe, "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) > 8000:
                content = content[:8000] + f"\n\n... (ตัดออก — ไฟล์ยาว {len(content)} chars)"
            return content
        except Exception as e:
            return f"[error] อ่านไฟล์ไม่ได้: {e}"

    def _safe_path(self, path: str) -> str | None:
        joined = os.path.abspath(os.path.join(WORKSPACE_DIR, path))
        if not joined.startswith(WORKSPACE_DIR):
            return None
        return joined

    def _list_files(self) -> str:
        files = []
        for root, _, fnames in os.walk(WORKSPACE_DIR):
            for f in fnames:
                rel = os.path.relpath(os.path.join(root, f), WORKSPACE_DIR)
                files.append(rel)
        return ", ".join(files[:20]) if files else ""
