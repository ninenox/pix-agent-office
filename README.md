# Pix Agent Office 🏢

> [🇹🇭 ภาษาไทย](README.th.md)

Pixel-art office dashboard — AI agents work in real-time, walking between rooms based on their task status.

<img src="examples/example.gif" width="100%" alt="Pix Agent Office">

## Quick Start

```bash
git clone https://github.com/ninenox/pix-agent-office.git
cd pix-agent-office
bash install.sh && source .venv/bin/activate
python main.py
```

Open: http://localhost:19000

## Modes

| Mode | How |
|------|-----|
| **Manual** | Type a task per agent → click ▶ RUN |
| **Auto** | Describe a goal → click ✦ BRAINSTORM → Boss AI assigns tasks |

## Agents (`config/team.json`)

Add, remove, or change agents by editing `team.json` — no code changes needed.

```json
"my-agent": {
  "name": "My Agent",
  "role": "Researcher",
  "model": "qwen2.5:7b",
  "provider": "ollama",
  "base_url": "http://localhost:11434/v1",
  "color": "#f97316",
  "system_prompt": "You are...",
  "tools": ["web_search", "read_file"]
}
```

Supported providers: `anthropic`, `openai`, `ollama`, or any OpenAI-compatible endpoint.

## Tools (`agents/tools/`)

| Tool | Description | Requires |
|------|-------------|----------|
| `read_file` | Read from `workspace/` | — |
| `write_file` | Write to `outputs/` | — |
| `run_python` | Run Python code | — |
| `http_request` | HTTP GET/POST/PUT/DELETE | — |
| `shell_command` | Run shell commands (blocked: rm, sudo, curl…) | — |
| `web_search` | Real-time web search | `BRAVE_API_KEY` |
| `google_calendar` | Fetch calendar events | OAuth setup |
| `telegram_notify` | Send Telegram messages | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| `create_schedule` | Schedule recurring agent tasks | — |

**Add a tool:** create `agents/tools/my_tool.py` extending `BaseTool` → restart.

## Scheduler

Agents can schedule themselves from a prompt:

> _"Show my Google Calendar every day at 10am and notify via Telegram"_

Schedules are stored in `config/schedules.json` and run automatically.

The `create_schedule` tool accepts:
- **Cron presets** — e.g. `"ทุกวัน 9 โมง"`, `"ทุกชั่วโมง"`
- **Raw cron expressions** — e.g. `"0 9 * * *"`, `"15 22 * * *"`

## Boss (Auto mode)

Configure in `team.json` under key `"boss"`:

```json
"boss": {
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "base_url": "http://localhost:11434/v1",
  "system_prompt": "You are the team lead..."
}
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/team` | Team config |
| GET | `/status` | All agent statuses |
| POST | `/status` | Update agent status |
| GET | `/status/<agent_id>` | Single agent status |
| POST | `/run` | Run agents |
| POST | `/brainstorm` | Auto mode |
| POST | `/stop` | Stop agents |
| GET | `/schedules` | List schedules |
| POST | `/schedules` | Create schedule |
| DELETE | `/schedules/<id>` | Delete schedule |
| POST | `/schedules/<id>/toggle` | Enable/disable schedule |
| GET | `/health` | Health check |

## License

MIT
