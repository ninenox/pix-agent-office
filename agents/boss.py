"""
Boss Agent — วิเคราะห์งานและแบ่งให้ทีม (Phase 1 เท่านั้น)
ไม่รัน team เอง — ให้ caller ทำ
"""

import anthropic
import json
import os
import re
import time

from agent_runner import update_office, load_team_config

client = anthropic.Anthropic(timeout=60.0)

BOSS_SYSTEM = """คุณคือ Team Lead ของทีม Claude Agent Office
วิเคราะห์งานที่ได้รับและตัดสินใจแบ่งงานให้ทีม

{team_desc}

กฎการแบ่งงาน:
1. ถ้างานชัดเจน ทำคนเดียวได้ → ส่งให้คนที่เหมาะที่สุดคนเดียว
2. ถ้างานซับซ้อน หลายด้าน → แตก subtask ให้ 2-3 คน แต่ละคนได้งานที่ชัดเจนและทำได้อิสระ
3. ไม่จำเป็นต้องใช้ทุกคน ใช้เท่าที่จำเป็นจริงๆ
4. แต่ละ task ต้องสมบูรณ์ในตัวเอง — agent จะไม่เห็นงานของคนอื่น

ตอบเป็น JSON เท่านั้น ห้ามมีข้อความอื่น:
{
  "plan": "อธิบาย strategy การแบ่งงาน (1 ประโยค)",
  "assignments": [
    {"agent_id": "claude-opus", "task": "รายละเอียดงาน"},
    {"agent_id": "claude-code", "task": "รายละเอียดงาน"}
  ]
}"""


def analyze_task(user_request: str) -> dict:
    """
    Boss วิเคราะห์งาน → คืน plan dict
    ไม่รัน team — caller ตัดสินใจเอง

    Returns:
        {
          "plan": str,
          "assignments": [{"agent_id": str, "task": str}, ...]
        }
    Raises:
        ValueError ถ้า parse plan ไม่ได้
    """
    config = load_team_config()

    # สร้าง team description จาก config
    team_desc = "ทีมของคุณ:\n" + "\n".join(
        f"- {agent_id} ({cfg.get('model','')}) : {cfg.get('role','')}"
        for agent_id, cfg in config.items()
    )
    system = BOSS_SYSTEM.format(team_desc=team_desc)

    # Set all agents to "thinking" ก่อน API call
    # → poll ถัดไปจะยืนยัน thinking แทนที่จะ override กลับ idle
    for agent_id in config.keys():
        update_office(agent_id, "thinking", "Boss กำลังวิเคราะห์...")

    print(f"\n[boss] Analyzing: {user_request[:60]}...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": f"งาน: {user_request}"}],
    )

    text = next((b.text for b in response.content if b.type == "text"), "")

    # ลอง parse JSON — strip markdown fences ถ้ามี
    cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Boss returned invalid JSON: {e}\nRaw: {text[:200]}") from e

    if "assignments" not in result:
        raise ValueError("Boss response missing 'assignments' key")

    # Validate agent IDs
    valid_ids = set(config.keys())
    result["assignments"] = [
        a for a in result["assignments"]
        if a.get("agent_id") in valid_ids and a.get("task")
    ]

    print(f"[boss] Plan: {result.get('plan', '')}")
    for a in result["assignments"]:
        print(f"  → [{a['agent_id']}] {a['task'][:60]}")

    return result
