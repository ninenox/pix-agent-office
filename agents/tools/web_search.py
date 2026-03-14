"""
Tool: web_search — ค้นหาข้อมูลจากเว็บ

ต้องการ BRAVE_API_KEY environment variable
สมัครฟรีได้ที่ https://brave.com/search/api/ (2,000 queries/เดือน)
"""

import os
import httpx
from .base import BaseTool


class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "ค้นหาข้อมูลจากเว็บ real-time "
        "ใช้สำหรับข้อมูลปัจจุบัน, ข่าว, หรือข้อมูลที่เปลี่ยนแปลงบ่อย "
        "ต้องการ BRAVE_API_KEY"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "คำค้นหา เช่น 'Python 3.13 features' หรือ 'ข่าว AI วันนี้'",
            },
            "count": {
                "type": "integer",
                "description": "จำนวนผลลัพธ์ (default: 5, max: 10)",
                "default": 5,
            },
        },
        "required": ["query"],
    }

    BRAVE_API = "https://api.search.brave.com/res/v1/web/search"

    def run(self, query: str, count: int = 5) -> str:
        api_key = os.environ.get("BRAVE_API_KEY", "").strip()
        if not api_key:
            return (
                "[error] BRAVE_API_KEY ไม่ได้ตั้งค่า\n"
                "สมัครฟรีได้ที่ https://brave.com/search/api/ แล้วตั้งค่า:\n"
                "  export BRAVE_API_KEY=BSA..."
            )

        count = min(max(1, count), 10)
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    self.BRAVE_API,
                    headers={
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip",
                        "X-Subscription-Token": api_key,
                    },
                    params={"q": query, "count": count},
                )
                response.raise_for_status()
                data = response.json()

            results = data.get("web", {}).get("results", [])
            if not results:
                return f"ไม่พบผลลัพธ์สำหรับ '{query}'"

            lines = [f"ผลการค้นหา: {query}\n"]
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. **{r.get('title', '')}**")
                lines.append(f"   {r.get('url', '')}")
                if r.get("description"):
                    lines.append(f"   {r['description']}")
                lines.append("")

            return "\n".join(lines).strip()

        except httpx.HTTPStatusError as e:
            return f"[error] Brave API: {e.response.status_code} {e.response.text[:200]}"
        except Exception as e:
            return f"[error] web_search ล้มเหลว: {e}"
