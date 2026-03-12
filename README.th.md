# Pixel Agent Office 🏢

> [🇬🇧 English](README.md)

Pixel-art office dashboard แสดง Claude AI team ทำงาน real-time
แต่ละ agent เดินไปโซนต่างๆ (โต๊ะ, กระดาน, break room) ตามสถานะงาน พร้อม waypoint pathfinding หลบกำแพงห้อง

**มี 2 Mode:**
- **Manual** — สั่งงาน agent ทีละตัว
- **Auto** — อธิบายงานครั้งเดียว Boss AI วิเคราะห์และแจกงานให้ทีมเอง

![Claude Agent Office](examples/example.gif)

---

## Quick Start

```bash
git clone https://github.com/ninenox/pixel-agent-office.git
cd pixel-agent-office
bash install.sh
source .venv/bin/activate
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

เปิดเบราว์เซอร์: http://localhost:19000

---

## วิธีใช้งาน

### ⚡ MANUAL Mode

กด **⚡ TASK DISPATCH** ที่ด้านบนของหน้าเว็บ → เลือก tab **⚙ MANUAL**

- พิมพ์งานในช่อง input ของแต่ละ agent
- กด **▶ RUN** เพื่อส่งงาน agent ทีละตัว หรือ `Ctrl+Enter`
- กด **🚀 DISPATCH ALL** เพื่อส่งงานทุก agent พร้อมกัน
- กด **■ STOP** หน้าชื่อ agent เพื่อหยุดงานนั้น หรือ **■ STOP ALL** เพื่อหยุดทุกตัว

### ✦ AUTO Mode (Brainstorm)

เลือก tab **✦ AUTO** ใน TASK DISPATCH:

- พิมพ์งานที่ต้องการในช่องเดียว
- กด **✦ BRAINSTORM** — Boss AI จะวิเคราะห์และแจกงานให้ทีมเอง
- agent ทุกตัวจะเดินไปที่ whiteboard ก่อน จากนั้น Boss จะแบ่งงาน
- ดู plan และ assignment ที่ Boss วางไว้ได้ในกล่องด้านล่างปุ่ม

### CLI

**รัน agents โดยไม่เปิด UI:**
```bash
python main.py --agents-only --tasks tasks.json
```

`tasks.json` ตัวอย่าง:
```json
{
  "claude-opus":   "วิเคราะห์แนวโน้ม AI Agent ปี 2026",
  "claude-sonnet": "ออกแบบ REST API สำหรับ task management",
  "claude-haiku":  "สรุปข่าวเทคโนโลยีวันนี้",
  "claude-code":   "เขียน unit test สำหรับ authentication"
}
```

**Single agent:**
```bash
cd agents
python agent_runner.py claude-sonnet "ออกแบบ database schema สำหรับ blog"
python agent_runner.py claude-haiku "สรุป 3 เทคนิค prompt engineering" --stream
```

---

## Agents

กำหนดได้ที่ `config/team.json` — เพิ่ม ลบ หรือแก้ไข agent ได้เลยโดยไม่ต้องแก้โค้ด

| Field | คำอธิบาย |
|-------|----------|
| `name` | ชื่อที่แสดงใน UI |
| `role` | คำอธิบายตำแหน่งสั้นๆ |
| `model` | Model ID ที่ใช้ |
| `provider` | `anthropic` \| `openai` \| `ollama` |
| `base_url` | API endpoint (สำหรับ ollama หรือ compatible API) |
| `color` | สีของ agent (hex) |
| `system_prompt` | System prompt กำหนดความสามารถและแนวทางการทำงาน |

### Provider ที่รองรับ

| Provider | API Key | หมายเหตุ |
|----------|---------|----------|
| `anthropic` | `ANTHROPIC_API_KEY` | Default |
| `openai` | `OPENAI_API_KEY` | GPT-4o, o1 ฯลฯ |
| `ollama` | — | รัน model ใน local |
| custom | `{PROVIDER}_API_KEY` | OpenAI-compatible endpoint อื่นๆ |

### ตัวอย่าง: เพิ่ม Ollama agent

```json
"qwen-local": {
  "name": "Qwen Local",
  "role": "Local Assistant",
  "model": "qwen2.5:7b",
  "provider": "ollama",
  "base_url": "http://localhost:11434/v1",
  "color": "#f59e0b",
  "system_prompt": "คุณคือ Local Assistant ชื่อ qwen-local..."
}
```

### ตัวอย่าง: เพิ่ม OpenAI agent

```json
"gpt-agent": {
  "name": "GPT Agent",
  "role": "OpenAI Assistant",
  "model": "gpt-4o",
  "provider": "openai",
  "color": "#10b981",
  "system_prompt": "คุณคือ OpenAI assistant ชื่อ gpt-agent..."
}
```

### กำหนด Boss (AUTO mode)

Boss ใช้ `claude-sonnet-4-6` เป็น default เปลี่ยนได้โดยเพิ่ม key `"boss"`:

```json
"boss": {
  "provider": "ollama",
  "model": "qwen2.5:14b",
  "base_url": "http://localhost:11434/v1"
}
```

---

## CLI Options

```
python main.py
  (ไม่มี flag)                    รัน server รอรับ task ผ่านหน้าเว็บ
  --agents-only --tasks <file>    รัน agents จากไฟล์ JSON (ไม่เปิด UI)
```

---

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | อ่านสถานะ agents ทั้งหมด |
| POST | `/status` | อัพเดตสถานะ agent |
| POST | `/run` | ส่ง tasks แล้วรัน agents ใน background |
| POST | `/brainstorm` | Boss วิเคราะห์งาน → แบ่งให้ทีม (AUTO mode) |
| POST | `/stop` | หยุด agent (ตั้งสถานะเป็น idle) |
| GET | `/health` | health check |

**POST `/run`:**
```json
{ "tasks": { "claude-opus": "วิเคราะห์...", "claude-sonnet": "ออกแบบ..." } }
```

**POST `/brainstorm`:**
```json
{ "task": "วิเคราะห์และออกแบบระบบ e-commerce" }
```

**POST `/stop`:**
```json
{ "agent_id": "claude-opus" }   // ละไว้ = หยุดทุกตัว
```

---

## Status → Zone

| Status | ห้อง | โซน |
|--------|------|-----|
| `writing` | Research | Desk |
| `coding` | Dev | Desk 1 |
| `researching` | Dev | Desk 2 |
| `thinking` / `planning` | Meeting | Whiteboard |
| `idle` / `error` | Break Room | — |

---

## License

MIT
