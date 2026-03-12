# Claude Agent Office 🏢

Pixel-art office dashboard แสดง Claude AI team ทำงาน real-time
แต่ละ agent เดินไปโซนต่างๆ (โต๊ะ, กระดาน, break room) ตามสถานะงาน 
มี 2 Mode:
1) Manual สั่งงาน agent ทีล่ะตัว
2) Auto สั่งงานครั้งเดียว agent จะประชุมและแบ่งงานกันทำเองตามเหมาะสม

![Claude Agent Office](images/example.png)

---

## Quick Start

```bash
git clone https://github.com/ninenox/claude-agent-office.git
cd claude-agent-office
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

กำหนดได้ที่ `config/team.json`

| Agent | บทบาท | Model |
|-------|--------|-------|
| `claude-opus` | Lead Researcher — วิเคราะห์เชิงลึก | claude-opus-4-6 |
| `claude-sonnet` | Code Architect — ออกแบบระบบ เขียนโค้ด | claude-sonnet-4-6 |
| `claude-haiku` | Quick Responder — ตอบเร็ว งานเบา | claude-haiku-4-5 |
| `claude-code` | Dev Agent — debug, refactor, test | claude-sonnet-4-6 |

เพิ่ม/แก้ไข agent ได้โดยแก้ไฟล์ `config/team.json`

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
