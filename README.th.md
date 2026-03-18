# Pix Agent Office 🏢

> [🇬🇧 English](README.md)

Pixel-art office dashboard — AI agents ทำงาน real-time เดินไปห้องต่างๆ ตามสถานะงาน

<img src="examples/example.gif" width="100%" alt="Pix Agent Office">

## เริ่มต้นใช้งาน

```bash
git clone https://github.com/ninenox/pix-agent-office.git
cd pix-agent-office
bash install.sh && source .venv/bin/activate
python main.py
```

เปิด: http://localhost:19000

## Mode การใช้งาน

| Mode | วิธี |
|------|------|
| **Manual** | พิมพ์ task ให้แต่ละ agent → กด ▶ RUN |
| **Auto** | อธิบายเป้าหมาย → กด ✦ BRAINSTORM → Boss AI แบ่งงานให้ทีม |

## Agents (`config/team.json`)

เพิ่ม ลบ หรือแก้ไข agent ได้ที่ `team.json` โดยไม่ต้องแก้โค้ด

```json
"my-agent": {
  "name": "My Agent",
  "role": "Researcher",
  "model": "qwen2.5:7b",
  "provider": "ollama",
  "base_url": "http://localhost:11434/v1",
  "color": "#f97316",
  "system_prompt": "คุณคือ...",
  "tools": ["web_search", "read_file"]
}
```

Provider ที่รองรับ: `anthropic`, `openai`, `ollama` หรือ OpenAI-compatible endpoint อื่นๆ

## Tools (`agents/tools/`)

| Tool | คำอธิบาย | ต้องการ |
|------|----------|---------|
| `read_file` | อ่านไฟล์จาก `workspace/` | — |
| `write_file` | เขียนไฟล์ไปที่ `outputs/` | — |
| `run_python` | รัน Python code | — |
| `http_request` | HTTP GET/POST/PUT/DELETE | — |
| `shell_command` | รัน shell command (บล็อก: rm, sudo, curl…) | — |
| `web_search` | ค้นหาเว็บ real-time | `BRAVE_API_KEY` |
| `google_calendar` | ดึงนัดหมายจาก Google Calendar | OAuth setup |
| `telegram_notify` | ส่งข้อความผ่าน Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| `create_schedule` | สร้าง recurring task ให้ agent | — |

**เพิ่ม tool ใหม่:** สร้าง `agents/tools/my_tool.py` extends `BaseTool` → restart

## Scheduler

Agent สามารถ schedule งานตัวเองได้จาก prompt:

> _"แสดงนัดหมายทุกวัน 10 โมงเช้าแล้วแจ้งผ่าน Telegram"_

Schedules เก็บใน `config/schedules.json` และรันอัตโนมัติตามเวลา

`create_schedule` รองรับ:
- **Cron presets** — เช่น `"ทุกวัน 9 โมง"`, `"ทุกชั่วโมง"`
- **Cron expression โดยตรง** — เช่น `"0 9 * * *"`, `"15 22 * * *"`

## Boss (Auto mode)

กำหนดใน `team.json` ด้วย key `"boss"`:

```json
"boss": {
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "base_url": "http://localhost:11434/v1",
  "system_prompt": "คุณคือ Team Lead..."
}
```

## API

| Method | Path | คำอธิบาย |
|--------|------|----------|
| GET | `/team` | Team config |
| GET | `/status` | สถานะ agents ทั้งหมด |
| POST | `/status` | อัปเดตสถานะ agent |
| GET | `/status/<agent_id>` | สถานะ agent คนเดียว |
| POST | `/run` | รัน agents |
| POST | `/brainstorm` | Auto mode |
| POST | `/stop` | หยุด agents |
| GET | `/schedules` | ดู schedules ทั้งหมด |
| POST | `/schedules` | สร้าง schedule |
| DELETE | `/schedules/<id>` | ลบ schedule |
| POST | `/schedules/<id>/toggle` | เปิด/ปิด schedule |
| GET | `/health` | Health check |

## License

MIT
