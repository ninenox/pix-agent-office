"""
Agent Runner — เรียก Claude API แล้วอัพเดทสถานะลง state.json
"""

import anthropic
import json
import os
import time
from filelock import FileLock

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "state.json")
TEAM_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "team.json")

client = anthropic.Anthropic(timeout=60.0)


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


def run_agent(agent_id: str, task: str, model: str = None, role: str = None):
    """
    รัน agent เดี่ยว — เรียก Claude API แล้วรายงานสถานะ

    Args:
        agent_id: ชื่อ agent เช่น "claude-opus"
        task: งานที่ต้องทำ
        model: model ที่ใช้ (ถ้าไม่ระบุจะอ่านจาก config)
        role: บทบาท (ถ้าไม่ระบุจะอ่านจาก config)
    """
    # โหลด config ถ้าไม่ได้ระบุ
    if not model or not role:
        config = load_team_config()
        agent_config = config.get(agent_id, {})
        model = model or agent_config.get("model", "claude-sonnet-4-6")
        role = role or agent_config.get("role", "AI assistant")

    try:
        # ขั้น 1: คิด
        update_office(agent_id, "thinking", "กำลังวิเคราะห์งาน...")
        time.sleep(0.5)

        # ขั้น 2: เรียก API
        update_office(agent_id, "researching", "กำลังประมวลผล...")

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=f"คุณคือ {role} ชื่อ {agent_id} ในทีม Claude Agent Office",
            messages=[{"role": "user", "content": task}],
        )

        # ขั้น 3: เขียนผลลัพธ์ (รองรับ thinking blocks)
        update_office(agent_id, "writing", "กำลังเขียนผลลัพธ์...")
        result = next((b.text for b in response.content if b.type == "text"), "")
        time.sleep(0.5)

        # ขั้น 4: เสร็จ
        tokens = response.usage.input_tokens + response.usage.output_tokens
        update_office(agent_id, "idle", f"เสร็จแล้ว ✓ ({tokens} tokens)")

        return result

    except Exception as e:
        print(f"\n  [{agent_id}] FULL ERROR: {e}")
        update_office(agent_id, "error", f"ผิดพลาด: {str(e)[:80]}")
        return None


def run_agent_stream(agent_id: str, task: str, model: str = None, role: str = None):
    """
    รัน agent แบบ streaming — อัพเดทสถานะ real-time ขณะ Claude พิมพ์
    """
    if not model or not role:
        config = load_team_config()
        agent_config = config.get(agent_id, {})
        model = model or agent_config.get("model", "claude-sonnet-4-6")
        role = role or agent_config.get("role", "AI assistant")

    try:
        update_office(agent_id, "thinking", "กำลังคิด...")

        with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=f"คุณคือ {role} ชื่อ {agent_id}",
            messages=[{"role": "user", "content": task}],
        ) as stream:

            update_office(agent_id, "writing", "กำลังเขียน...")
            full_text = ""
            for text in stream.text_stream:
                full_text += text
                if len(full_text) % 80 < 5:
                    preview = full_text[-40:].replace("\n", " ")
                    update_office(agent_id, "writing", f"...{preview}")

        update_office(agent_id, "idle", f"เสร็จ ({len(full_text)} chars)")
        return full_text

    except Exception as e:
        print(f"\n  [{agent_id}] FULL ERROR: {e}")
        update_office(agent_id, "error", f"ผิดพลาด: {str(e)[:80]}")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run a single Claude agent")
    parser.add_argument("agent_id", help="Agent ID เช่น claude-opus")
    parser.add_argument("task", help="งานที่ต้องทำ")
    parser.add_argument("--stream", action="store_true", help="ใช้ streaming mode")
    args = parser.parse_args()

    if args.stream:
        result = run_agent_stream(args.agent_id, args.task)
    else:
        result = run_agent(args.agent_id, args.task)

    if result:
        print(f"\n{'='*60}")
        print(result[:500])
