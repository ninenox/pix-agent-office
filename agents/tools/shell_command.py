"""
Tool: shell_command — รัน shell command และคืน output
"""

import os
import subprocess
from .base import BaseTool

# คำสั่งที่ห้ามใช้เด็ดขาด
_BLOCKED = {
    "rm", "rmdir", "del", "format", "mkfs",
    "dd", "shutdown", "reboot", "halt", "poweroff",
    "sudo", "su", "chmod", "chown", "chroot",
    "curl", "wget", "nc", "netcat", "ncat",
    "python", "python3", "pip", "pip3",
    "> /", ">/",
}

TIMEOUT = 15  # seconds


class ShellCommandTool(BaseTool):
    name = "shell_command"
    description = (
        "รัน shell command และคืน stdout/stderr "
        "ใช้สำหรับดูไฟล์, ค้นหาข้อมูล, รัน script, จัดการ process "
        "timeout 15 วินาที ไม่อนุญาตคำสั่งอันตราย (rm, sudo, curl ฯลฯ)"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command ที่ต้องการรัน เช่น 'ls -la', 'cat file.txt', 'grep pattern dir/'",
            },
        },
        "required": ["command"],
    }

    def run(self, command: str) -> str:
        # ตรวจสอบคำสั่งอันตราย
        cmd_lower = command.lower().strip()
        first_word = cmd_lower.split()[0] if cmd_lower.split() else ""
        if first_word in _BLOCKED or any(b in cmd_lower for b in {"> /", ">/"} ):
            return f"[error] คำสั่ง '{first_word}' ไม่อนุญาต"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                cwd=os.path.expanduser("~"),
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if result.returncode != 0:
                return f"[exit {result.returncode}]\n{stderr or stdout or '(no output)'}"
            if stderr:
                return f"{stdout}\n[stderr]\n{stderr}".strip()
            return stdout or "(รันสำเร็จ — ไม่มี output)"

        except subprocess.TimeoutExpired:
            return f"[error] timeout หลัง {TIMEOUT}s"
        except Exception as e:
            return f"[error] รันไม่ได้: {e}"
