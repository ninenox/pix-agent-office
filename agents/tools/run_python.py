"""
Tool: run_python — รัน Python code และคืน output
"""

import os
import subprocess
import sys
import tempfile
from .base import BaseTool


class RunPythonTool(BaseTool):
    name = "run_python"
    description = (
        "รัน Python code และคืน stdout/stderr "
        "ใช้สำหรับคำนวณ, ประมวลผลข้อมูล, หรือทดสอบ logic "
        "timeout 15 วินาที ไม่มี network access"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code ที่ต้องการรัน",
            },
        },
        "required": ["code"],
    }

    TIMEOUT = 15  # seconds

    def run(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmpfile = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmpfile],
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if result.returncode != 0:
                return f"[exit {result.returncode}]\n{stderr or stdout or '(no output)'}"
            if stderr:
                return f"{stdout}\n[stderr]\n{stderr}".strip()
            return stdout or "(รันสำเร็จ — ไม่มี output)"

        except subprocess.TimeoutExpired:
            return f"[error] timeout หลัง {self.TIMEOUT}s"
        except Exception as e:
            return f"[error] รันไม่ได้: {e}"
        finally:
            os.unlink(tmpfile)
