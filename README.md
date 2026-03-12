# Claude Agent Office 🏢

A pixel-art office dashboard that visualizes your Claude AI team working in real-time. Inspired by [Star-Office-UI](https://github.com/ringhyacinth/Star-Office-UI).

Each Claude agent appears as a pixel character that walks between office zones (desk, whiteboard, breakroom) based on their current task status.

## Features

- **Pixel Office Canvas** — hand-drawn office with desks, whiteboard, bookshelf, coffee machine
- **4 AI Agents** — Opus (research), Sonnet (code), Haiku (quick tasks), Code (dev)
- **Real-time Status** — agents move to zones matching their work status
- **Activity Log** — sidebar shows all status changes with timestamps
- **Multi-Agent** — run multiple Claude instances simultaneously via API
- **Boss Router** — auto-delegate tasks to the right agent
- **Demo Mode** — works without API key (auto-simulates activity)

---

## Installation

**Prerequisites:** Python 3.10+, macOS หรือ Linux

```bash
git clone https://github.com/ninenox/claude-agent-office.git
cd claude-agent-office
bash install.sh
```

script จะทำขั้นตอนต่อไปนี้อัตโนมัติ:

1. ตรวจสอบ OS และ Python version (ต้องการ 3.10+)
2. ใช้ `uv` ถ้ามีติดตั้งอยู่ ไม่งั้น fallback เป็น `pip`
3. สร้าง `.venv` (virtual environment)
4. ติดตั้ง dependencies จาก `backend/requirements.txt`
5. สร้าง `state.json` จาก template
6. แจ้งเตือนถ้ายังไม่มี `ANTHROPIC_API_KEY`

**ตัวอย่าง output เมื่อติดตั้งสำเร็จ:**

```
🏢 Claude Agent Office — Setup

  ✓ OS: macOS
  ✓ Python 3.12
  ⚠ ไม่พบ uv — จะใช้ pip แทน
  ✓ สร้าง .venv เรียบร้อย
  ✓ Activated: .venv
  ✓ ติดตั้ง dependencies เสร็จแล้ว
  ✓ สร้าง state.json จาก template

  ⚠ ยังไม่มี ANTHROPIC_API_KEY — รันได้แค่ demo mode

✅ ติดตั้งสำเร็จ!
```

หลังติดตั้ง ให้ activate venv ก่อนใช้งานทุกครั้ง:

```bash
source .venv/bin/activate
```

> **ต้องการ API key หรือไม่?** — ไม่จำเป็นสำหรับ demo mode
> สำหรับ full mode ให้ตั้งค่า: `export ANTHROPIC_API_KEY=sk-ant-...`

---

## Running

### Mode 1 — Demo (no API key required)

เปิด server อย่างเดียว agents จะ simulate การทำงานอัตโนมัติในหน้าเว็บ

```bash
python main.py --server-only
```

เปิดเบราว์เซอร์: http://localhost:19000

---

### Mode 2 — Full (server + agents จริง)

ต้องมี Anthropic API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# รัน server + agents พร้อมกัน (ใช้ demo tasks ในตัว)
python main.py
```

agents จะเริ่มทำงานจริงผ่าน Claude API และอัพเดตสถานะบนหน้าจอ real-time

---

### Mode 3 — Custom Tasks

กำหนด tasks ของแต่ละ agent เองผ่านไฟล์ JSON

**สร้างไฟล์ tasks เช่น `my_tasks.json`:**

```json
{
  "claude-opus":   "วิเคราะห์แนวโน้ม AI Agent ปี 2026 และสรุป 5 ประเด็นหลัก",
  "claude-sonnet": "ออกแบบ REST API สำหรับระบบ task management พร้อม OpenAPI spec",
  "claude-haiku":  "สรุปข่าวเทคโนโลยีวันนี้เป็น bullet points 5 ข้อ",
  "claude-code":   "เขียน unit test สำหรับ user authentication ด้วย pytest"
}
```

```bash
python main.py --tasks my_tasks.json
```

---

### Mode 4 — Boss Router (auto-delegate)

ให้ Boss Agent วิเคราะห์ request แล้วแจกงานให้ลูกทีมเองอัตโนมัติ

```bash
export ANTHROPIC_API_KEY=sk-ant-...

cd agents
python router.py "วิเคราะห์และออกแบบระบบ e-commerce ทั้งหมด"
```

---

### Mode 5 — Single Agent

รัน agent ตัวเดียวโดยตรง

```bash
cd agents

# แบบปกติ
python agent_runner.py claude-sonnet "ออกแบบ database schema สำหรับ blog platform"

# แบบ streaming (เห็นผลทีละ token)
python agent_runner.py claude-haiku "สรุป 3 เทคนิค prompt engineering" --stream
```

---

### Mode 6 — Agent with Tools

รัน agent ที่สามารถใช้ tools ได้ (web_search, write_file, read_file)

```bash
cd agents
python agent_tools.py claude-code "ค้นหาข้อมูลเกี่ยวกับ FastAPI แล้วเขียนสรุปลงไฟล์ summary.md"
```

ผลลัพธ์จะถูกบันทึกใน `outputs/`

---

### Mode 7 — Manual Status Control

เปลี่ยนสถานะ agent ด้วยมือโดยไม่ต้องเรียก API (ใช้กับ demo หรือ testing)

```bash
python set_state.py claude-opus writing "กำลังเขียนรายงาน"
python set_state.py claude-haiku idle "Coffee break"
python set_state.py claude-sonnet coding "Fixing bug #42"
python set_state.py claude-code error "Build failed"
```

---

## CLI Reference

```
python main.py [options]

Options:
  (ไม่มี flag)          รัน server + agents พร้อมกัน (ใช้ default demo tasks)
  --server-only         รัน Flask server อย่างเดียว (demo mode, ไม่ต้องมี API key)
  --agents-only         รัน agents อย่างเดียว (ไม่มี UI server)
  --tasks <file.json>   ระบุไฟล์ JSON กำหนด tasks ของแต่ละ agent
```

```
python set_state.py <agent_id> <status> [detail]

agent_id:  claude-opus | claude-sonnet | claude-haiku | claude-code
status:    writing | coding | researching | thinking | planning | idle | error | syncing
detail:    ข้อความแสดงรายละเอียด (optional)
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | หน้า dashboard |
| GET | `/status` | อ่านสถานะ agents ทั้งหมด |
| GET | `/status/<agent_id>` | อ่านสถานะ agent ตัวเดียว |
| POST | `/status` | อัพเดตสถานะ agent |
| GET | `/health` | health check |

**POST `/status` body:**
```json
{
  "agent_id": "claude-opus",
  "status": "writing",
  "detail": "กำลังเขียนรายงาน"
}
```

---

## Architecture

```
main.py
    │
    ├─ Thread → Flask server (port 19000)
    │               └─ serves frontend/
    │               └─ GET/POST /status ↔ state.json
    │
    └─ agents/orchestrator.py
            ├─ Thread 1 → claude-opus   → Anthropic API ─┐
            ├─ Thread 2 → claude-sonnet → Anthropic API ─┤  write
            ├─ Thread 3 → claude-haiku  → Anthropic API ─┤  state.json
            └─ Thread 4 → claude-code   → Anthropic API ─┘

Browser (poll every 2s)
    └─ GET /status → parse state.json → move pixel characters
```

---

## Agent Modes

| Mode | File | Description |
|------|------|-------------|
| Basic | `agents/agent_runner.py` | Simple API call + status update |
| Stream | `agents/agent_runner.py --stream` | Streaming พร้อม real-time preview |
| Tools | `agents/agent_tools.py` | Agent ที่ใช้ tools ได้ (search, file I/O) |
| Multi | `agents/orchestrator.py` | รัน agents ทั้งทีมพร้อมกัน |
| Router | `agents/router.py` | Boss agent แจกงานให้ลูกทีมอัตโนมัติ |

---

## Configuration

| ไฟล์ | หน้าที่ |
|------|---------|
| `config/team.json` | ชื่อ, role, model ของแต่ละ agent |
| `config/zones.json` | mapping status → ตำแหน่งบน canvas |
| `state.sample.json` | template สถานะเริ่มต้น |
| `state.json` | สถานะ runtime (สร้างอัตโนมัติ) |

---

## Status → Zone Mapping

| Status | Zone | Icon |
|--------|------|------|
| `writing` | Desk 1 | ✍️ |
| `coding` | Desk 2 | 💻 |
| `researching` | Desk 3 | 🔍 |
| `thinking` | Whiteboard | 🧠 |
| `planning` | Whiteboard | 📋 |
| `idle` | Breakroom | ☕ |
| `error` | Breakroom | ⚠️ |
| `syncing` | Desk 1 | 🔄 |

---

## License

MIT
