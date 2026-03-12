"""
Router — Boss Agent ที่วิเคราะห์งานแล้วแจกให้ลูกทีมอัตโนมัติ
"""

import anthropic
import json
import os
import time
from agent_runner import update_office, load_team_config
from orchestrator import run_team

client = anthropic.Anthropic()


def route_and_run(user_request: str):
    """
    ให้ Boss Agent วิเคราะห์ request แล้วแจกงานให้ลูกทีม

    Args:
        user_request: คำขอจาก user
    """
    config = load_team_config()

    # สร้างรายละเอียดทีม
    team_desc = "\n".join(
        f"- {aid}: {info['role']} (model: {info['model']})"
        for aid, info in config.items()
    )

    update_office("router", "thinking", "Boss กำลังวิเคราะห์งาน...")

    router_model = config.get("claude-sonnet", {}).get("model", "claude-sonnet-4-6")

    response = client.messages.create(
        model=router_model,
        max_tokens=2048,
        system=f"""คุณคือ Team Lead ของ Claude Agent Office
มีลูกทีมดังนี้:
{team_desc}

วิเคราะห์ request แล้วตอบเป็น JSON เท่านั้น:
{{
  "plan": "อธิบายแผนสั้นๆ",
  "assignments": [
    {{"agent_id": "claude-opus", "task": "งานที่มอบหมาย"}},
    ...
  ]
}}

กฎ:
- แจกงานให้ agent ที่เหมาะสมกับ role
- ไม่จำเป็นต้องใช้ทุกตัว
- task ต้องชัดเจนและเฉพาะเจาะจง""",
        messages=[{"role": "user", "content": user_request}],
    )

    # Parse response
    try:
        text = response.content[0].text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if len(lines) > 1:
                text = "\n".join(lines[1:]).rsplit("```", 1)[0].strip()
        plan = json.loads(text)
    except (json.JSONDecodeError, IndexError) as e:
        update_office("router", "error", f"Parse error: {e}")
        print(f"[router] Failed to parse plan: {text[:200]}")
        return None

    # แสดงแผน
    print(f"\n{'='*60}")
    print(f"  Boss Plan: {plan.get('plan', 'N/A')}")
    print(f"{'='*60}")

    assignments = plan.get("assignments", [])
    for a in assignments:
        print(f"  → [{a['agent_id']}] {a['task'][:60]}")

    update_office("router", "planning", f"แจกงาน {len(assignments)} agents")

    # แปลงเป็น tasks dict แล้วรัน
    tasks = {a["agent_id"]: a["task"] for a in assignments}
    results = run_team(tasks)

    update_office("router", "idle", f"ทีมทำงานเสร็จ ✓")
    return {"plan": plan, "results": results}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("request", help="งานที่ต้องการให้ทีมทำ")
    args = parser.parse_args()

    route_and_run(args.request)
