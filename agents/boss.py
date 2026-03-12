"""
Boss Agent — วิเคราะห์งานและแบ่งให้ทีม (Phase 1 เท่านั้น)
ไม่รัน team เอง — ให้ caller ทำ
"""

import json
import re

from agent_runner import update_office, load_team_config, get_anthropic_client, get_openai_compatible_client

# Boss ใช้ config จาก team.json key "boss" ถ้ามี ไม่งั้น default anthropic
BOSS_DEFAULT_PROVIDER = "anthropic"
BOSS_DEFAULT_MODEL    = "claude-sonnet-4-6"
BOSS_DEFAULT_BASE_URL = "http://localhost:11434/v1"

BOSS_SYSTEM = """คุณคือ Team Lead ของทีม Claude Agent Office
วิเคราะห์งานที่ได้รับและตัดสินใจแบ่งงานให้ทีม

{team_desc}

กฎการแบ่งงาน:
1. ถ้างานชัดเจน ทำคนเดียวได้ → ส่งให้คนที่เหมาะที่สุดคนเดียว
2. ถ้างานซับซ้อน หลายด้าน → แตก subtask ให้ 2-3 คน แต่ละคนได้งานที่ชัดเจนและทำได้อิสระ
3. ไม่จำเป็นต้องใช้ทุกคน ใช้เท่าที่จำเป็นจริงๆ
4. แต่ละ task ต้องสมบูรณ์ในตัวเอง — agent จะไม่เห็นงานของคนอื่น

ตอบเป็น JSON เท่านั้น ห้ามมีข้อความอื่น:
{{
  "plan": "อธิบาย strategy การแบ่งงาน (1 ประโยค)",
  "assignments": [
    {{"agent_id": "claude-opus", "task": "รายละเอียดงาน"}},
    {{"agent_id": "claude-code", "task": "รายละเอียดงาน"}}
  ]
}}"""


def _get_boss_config() -> tuple[str, str, str]:
    """อ่าน boss config จาก team.json (key "boss") ถ้ามี"""
    config = load_team_config()
    boss_cfg = config.get("boss", {})
    provider = boss_cfg.get("provider", BOSS_DEFAULT_PROVIDER)
    model    = boss_cfg.get("model",    BOSS_DEFAULT_MODEL)
    base_url = boss_cfg.get("base_url", BOSS_DEFAULT_BASE_URL)
    return provider, model, base_url


def _call_boss_api(system: str, user_msg: str, provider: str, model: str, base_url: str) -> str:
    if provider != "anthropic":
        client = get_openai_compatible_client(provider, base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_msg},
            ],
        )
        return response.choices[0].message.content or ""
    else:
        client = get_anthropic_client()
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return next((b.text for b in response.content if b.type == "text"), "")


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
    provider, model, base_url = _get_boss_config()
    config = load_team_config()

    # สร้าง team description — ไม่รวม key "boss"
    team_desc = "ทีมของคุณ:\n" + "\n".join(
        f"- {agent_id} ({cfg.get('model','')}) : {cfg.get('role','')}"
        for agent_id, cfg in config.items()
        if agent_id != "boss"
    )
    system = BOSS_SYSTEM.format(team_desc=team_desc)

    # Set all agents to "thinking" ก่อน API call
    for agent_id in config.keys():
        if agent_id != "boss":
            update_office(agent_id, "thinking", "Boss กำลังวิเคราะห์...")

    print(f"\n[boss] Analyzing via {provider}/{model}: {user_request[:60]}...")

    text = _call_boss_api(system, f"งาน: {user_request}", provider, model, base_url)

    # ลอง parse JSON — strip markdown fences ถ้ามี
    cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Boss returned invalid JSON: {e}\nRaw: {text[:200]}") from e

    if "assignments" not in result:
        raise ValueError("Boss response missing 'assignments' key")

    # Validate agent IDs (ไม่รวม boss)
    valid_ids = {k for k in config.keys() if k != "boss"}
    result["assignments"] = [
        a for a in result["assignments"]
        if a.get("agent_id") in valid_ids and a.get("task")
    ]

    print(f"[boss] Plan: {result.get('plan', '')}")
    for a in result["assignments"]:
        print(f"  → [{a['agent_id']}] {a['task'][:60]}")

    return result
