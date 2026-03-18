"""
Tool: google_calendar — ดึงนัดหมายจาก Google Calendar

Setup:
  1. ไปที่ https://console.cloud.google.com/
  2. สร้าง Project → เปิด Google Calendar API
  3. สร้าง OAuth 2.0 Client ID (Desktop app) → download เป็น credentials.json
  4. วาง credentials.json ไว้ที่ config/google_credentials.json
  5. รันครั้งแรกจะเปิดเบราว์เซอร์ให้ authorize → สร้าง config/google_token.json อัตโนมัติ
"""

import json
import os
from datetime import datetime, timezone, timedelta
from .base import BaseTool

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config"))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "google_credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "google_token.json")
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_service():
    """สร้าง Google Calendar service พร้อม OAuth2"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "ไม่พบ config/google_credentials.json — "
                    "ดาวน์โหลดจาก Google Cloud Console แล้ววางไว้ที่ config/"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


class GoogleCalendarTool(BaseTool):
    name = "google_calendar"
    description = (
        "ดึงนัดหมายจาก Google Calendar "
        "แสดงรายการ events ในช่วงเวลาที่กำหนด "
        "ต้องมี config/google_credentials.json ก่อนใช้งาน"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "description": "จำนวนวันที่ต้องการดู นับจากวันนี้ (default: 7)",
                "default": 7,
            },
            "max_results": {
                "type": "integer",
                "description": "จำนวน events สูงสุดที่แสดง (default: 20)",
                "default": 20,
            },
            "calendar_id": {
                "type": "string",
                "description": "Calendar ID (default: 'primary' = ปฏิทินหลัก)",
                "default": "primary",
            },
        },
        "required": [],
    }

    def run(
        self,
        days: int = 7,
        max_results: int = 20,
        calendar_id: str = "primary",
    ) -> str:
        try:
            service = _get_service()
        except FileNotFoundError as e:
            return f"[error] {e}"
        except Exception as e:
            return f"[error] เชื่อมต่อ Google Calendar ไม่ได้: {e}"

        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days)).isoformat()

        try:
            result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
        except Exception as e:
            return f"[error] ดึงข้อมูลไม่ได้: {e}"

        events = result.get("items", [])
        if not events:
            return f"ไม่มีนัดหมายใน {days} วันข้างหน้า"

        lines = [f"นัดหมาย {days} วันข้างหน้า ({len(events)} รายการ):\n"]
        for ev in events:
            start = ev["start"].get("dateTime") or ev["start"].get("date", "")
            # แปลงเวลาให้อ่านง่าย
            try:
                dt = datetime.fromisoformat(start)
                if dt.tzinfo:
                    dt = dt.astimezone()
                start_str = dt.strftime("%d/%m %H:%M") if "T" in start else dt.strftime("%d/%m")
            except Exception:
                start_str = start

            title = ev.get("summary", "(ไม่มีชื่อ)")
            location = ev.get("location", "")
            loc_str = f" 📍 {location}" if location else ""
            lines.append(f"• {start_str} — {title}{loc_str}")

        return "\n".join(lines)
