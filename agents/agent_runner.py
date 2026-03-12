"""
Agent Runner — เรียก Claude API, OpenAI API, หรือ Ollama แล้วอัพเดทสถานะลง state.json
"""

import anthropic
import httpx
import json
import os
import time
from filelock import FileLock

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "state.json")
TEAM_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "team.json")

_anthropic_client = None


def get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(timeout=httpx.Timeout(600.0, connect=10.0))
    return _anthropic_client


def get_openai_compatible_client(provider: str, base_url: str = None):
    """
    คืน OpenAI client สำหรับ provider ที่ใช้ OpenAI-compatible API:
      - openai  → api_key จาก OPENAI_API_KEY, base_url default (api.openai.com)
      - ollama  → api_key="ollama", base_url=localhost:11434
      - อื่นๆ   → base_url และ api_key จาก env PROVIDER_API_KEY
    """
    from openai import OpenAI

    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        return OpenAI(api_key=api_key, base_url=base_url or None)

    if provider == "ollama":
        return OpenAI(
            api_key="ollama",
            base_url=base_url or "http://localhost:11434/v1",
        )

    # generic OpenAI-compatible (เช่น LM Studio, Together AI ฯลฯ)
    env_key = f"{provider.upper()}_API_KEY"
    api_key = os.environ.get(env_key, "none")
    return OpenAI(api_key=api_key, base_url=base_url)


def load_team_config():
    """โหลดข้อมูลทีมจาก config/team.json"""
    with open(TEAM_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def update_office(agent_id: str, status: str, detail: str):
    """เขียนสถานะลง state.json (thread-safe)"""
    lock = FileLock(STATE_FILE + ".lock")
    with lock:
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {"agents": {}}

        if "agents" not in state:
            state["agents"] = {}

        state["agents"][agent_id] = {
            "status": status,
            "detail": detail,
            "updated_at": time.strftime("%H:%M:%S"),
        }

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"  [{agent_id}] {status}: {detail}")


def _call_anthropic(agent_id: str, task: str, model: str, role: str) -> str:
    client = get_anthropic_client()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=f"คุณคือ {role} ชื่อ {agent_id} ในทีม Claude Agent Office",
        messages=[{"role": "user", "content": task}],
    )
    return next((b.text for b in response.content if b.type == "text"), "")


def _call_openai_compatible(agent_id: str, task: str, model: str, role: str,
                             provider: str, base_url: str) -> str:
    client = get_openai_compatible_client(provider, base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"คุณคือ {role} ชื่อ {agent_id} ในทีม Claude Agent Office"},
            {"role": "user",   "content": task},
        ],
    )
    return response.choices[0].message.content or ""


def run_agent(agent_id: str, task: str, model: str = None, role: str = None,
              provider: str = None, base_url: str = None):
    """
    รัน agent เดี่ยว — รองรับ provider: anthropic | openai | ollama
    """
    if not model or not role or not provider:
        config = load_team_config()
        agent_config = config.get(agent_id, {})
        model    = model    or agent_config.get("model",    "claude-sonnet-4-6")
        role     = role     or agent_config.get("role",     "AI assistant")
        provider = provider or agent_config.get("provider", "anthropic")
        base_url = base_url or agent_config.get("base_url")

    try:
        update_office(agent_id, "thinking", "กำลังวิเคราะห์งาน...")
        time.sleep(0.5)

        update_office(agent_id, "researching", f"กำลังประมวลผล [{provider}]...")

        if provider == "anthropic":
            result = _call_anthropic(agent_id, task, model, role)
        else:
            result = _call_openai_compatible(agent_id, task, model, role, provider, base_url)

        update_office(agent_id, "writing", "กำลังเขียนผลลัพธ์...")
        time.sleep(0.5)

        update_office(agent_id, "idle", f"เสร็จแล้ว ✓ [{provider}]")
        return result

    except Exception as e:
        print(f"\n  [{agent_id}] FULL ERROR: {e}")
        update_office(agent_id, "error", f"ผิดพลาด: {str(e)[:80]}")
        return None


def run_agent_stream(agent_id: str, task: str, model: str = None, role: str = None,
                     provider: str = None, base_url: str = None):
    """
    รัน agent แบบ streaming — รองรับ provider: anthropic | openai | ollama
    """
    if not model or not role or not provider:
        config = load_team_config()
        agent_config = config.get(agent_id, {})
        model    = model    or agent_config.get("model",    "claude-sonnet-4-6")
        role     = role     or agent_config.get("role",     "AI assistant")
        provider = provider or agent_config.get("provider", "anthropic")
        base_url = base_url or agent_config.get("base_url")

    try:
        update_office(agent_id, "thinking", "กำลังคิด...")
        full_text = ""

        if provider == "anthropic":
            client = get_anthropic_client()
            with client.messages.stream(
                model=model,
                max_tokens=4096,
                system=f"คุณคือ {role} ชื่อ {agent_id}",
                messages=[{"role": "user", "content": task}],
            ) as stream:
                update_office(agent_id, "writing", "กำลังเขียน...")
                for text in stream.text_stream:
                    full_text += text
                    if len(full_text) % 80 < 5:
                        preview = full_text[-40:].replace("\n", " ")
                        update_office(agent_id, "writing", f"...{preview}")
        else:
            client = get_openai_compatible_client(provider, base_url)
            update_office(agent_id, "writing", "กำลังเขียน...")
            with client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"คุณคือ {role} ชื่อ {agent_id}"},
                    {"role": "user",   "content": task},
                ],
                stream=True,
            ) as stream:
                for chunk in stream:
                    text = chunk.choices[0].delta.content or ""
                    full_text += text
                    if len(full_text) % 80 < 5:
                        preview = full_text[-40:].replace("\n", " ")
                        update_office(agent_id, "writing", f"...{preview}")

        update_office(agent_id, "idle", f"เสร็จ ({len(full_text)} chars) [{provider}]")
        return full_text

    except Exception as e:
        print(f"\n  [{agent_id}] FULL ERROR: {e}")
        update_office(agent_id, "error", f"ผิดพลาด: {str(e)[:80]}")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run a single agent")
    parser.add_argument("agent_id", help="Agent ID เช่น claude-opus")
    parser.add_argument("task",     help="งานที่ต้องทำ")
    parser.add_argument("--stream", action="store_true", help="ใช้ streaming mode")
    args = parser.parse_args()

    if args.stream:
        result = run_agent_stream(args.agent_id, args.task)
    else:
        result = run_agent(args.agent_id, args.task)

    if result:
        print(f"\n{'='*60}")
        print(result[:500])
