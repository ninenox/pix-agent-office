"""
Tool: telegram_notify — ส่งข้อความผ่าน Telegram Bot

Setup:
  1. สร้าง bot ผ่าน @BotFather → ได้ BOT_TOKEN
  2. ส่งข้อความหา bot ของตัวเอง แล้วเปิด:
     https://api.telegram.org/bot<TOKEN>/getUpdates
     → หา chat_id ในผลลัพธ์
  3. ตั้ง env vars:
     export TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
     export TELEGRAM_CHAT_ID=123456789
"""

import os
import httpx
from .base import BaseTool

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifyTool(BaseTool):
    name = "telegram_notify"
    description = (
        "ส่งข้อความแจ้งเตือนผ่าน Telegram "
        "ใช้สำหรับส่งผลลัพธ์, สรุปรายงาน หรือแจ้งเตือนเมื่องานเสร็จ "
        "ต้องตั้ง TELEGRAM_BOT_TOKEN และ TELEGRAM_CHAT_ID ใน environment"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "ข้อความที่ต้องการส่ง รองรับ Markdown",
            },
            "chat_id": {
                "type": "string",
                "description": "Telegram Chat ID (optional — ใช้ TELEGRAM_CHAT_ID จาก env ถ้าไม่ระบุ)",
            },
        },
        "required": ["message"],
    }

    TIMEOUT = 10

    def run(self, message: str, chat_id: str = None, **kwargs) -> str:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            return "[error] ไม่พบ TELEGRAM_BOT_TOKEN ใน environment"

        target_chat = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
        if not target_chat:
            return "[error] ไม่พบ TELEGRAM_CHAT_ID ใน environment"

        url = TELEGRAM_API.format(token=token)
        payload = {
            "chat_id": target_chat,
            "text": message,
            "parse_mode": "Markdown",
        }

        try:
            resp = httpx.post(url, json=payload, timeout=self.TIMEOUT)
            if resp.status_code == 200:
                return f"✓ ส่งข้อความ Telegram สำเร็จ ({len(message)} chars)"
            data = resp.json()
            return f"[error] Telegram API: {data.get('description', resp.status_code)}"
        except httpx.TimeoutException:
            return f"[error] timeout หลัง {self.TIMEOUT}s"
        except Exception as e:
            return f"[error] ส่งไม่ได้: {e}"
