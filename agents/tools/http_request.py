"""
Tool: http_request — เรียก HTTP GET/POST ภายนอก
"""

import json
import httpx
from .base import BaseTool


class HttpRequestTool(BaseTool):
    name = "http_request"
    description = (
        "เรียก HTTP request ไปยัง URL ภายนอก "
        "ใช้สำหรับดึงข้อมูลจาก API หรือ webhook "
        "คืน response body สูงสุด 5000 chars"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE"],
                "description": "HTTP method",
            },
            "url": {
                "type": "string",
                "description": "URL เต็มรูปแบบ เช่น https://api.example.com/data",
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers เพิ่มเติม (optional)",
            },
            "body": {
                "type": "object",
                "description": "JSON body สำหรับ POST/PUT (optional)",
            },
            "params": {
                "type": "object",
                "description": "Query parameters (optional)",
            },
        },
        "required": ["method", "url"],
    }

    TIMEOUT = 15
    MAX_RESPONSE = 5000

    def run(
        self,
        method: str,
        url: str,
        headers: dict = None,
        body: dict = None,
        params: dict = None,
    ) -> str:
        try:
            with httpx.Client(timeout=self.TIMEOUT, follow_redirects=True) as client:
                kwargs: dict = {
                    "headers": headers or {},
                    "params": params or {},
                }
                if body and method.upper() in ("POST", "PUT", "PATCH"):
                    kwargs["json"] = body

                response = getattr(client, method.lower())(url, **kwargs)

            # พยายาม parse JSON ก่อน แล้วค่อย fallback เป็น text
            try:
                data = response.json()
                text = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                text = response.text

            if len(text) > self.MAX_RESPONSE:
                text = text[: self.MAX_RESPONSE] + f"\n... (ตัดออก — response ยาว {len(text)} chars)"

            return f"[{response.status_code} {response.reason_phrase}]\n{text}"

        except httpx.TimeoutException:
            return f"[error] timeout หลัง {self.TIMEOUT}s"
        except httpx.RequestError as e:
            return f"[error] request ล้มเหลว: {e}"
        except Exception as e:
            return f"[error] {e}"
