"""
Agent Tools — รัน agent พร้อม tool-use loop

ใช้ ToolRegistry จาก tools/ ซึ่ง auto-discover tools ทั้งหมด
เพิ่ม tool ใหม่: สร้างไฟล์ใน agents/tools/ แล้ว restart เท่านั้น

การกำหนด tools ต่อ agent ใน team.json:
  "tools": ["all"]                          ← ทุก tool
  "tools": ["web_search", "read_file"]      ← เฉพาะที่ระบุ
  (ไม่มี tools field)                       ← ไม่ใช้ tool ใดเลย
"""

import json
import os
import sys
import time

# ให้ import ได้ทั้งจาก agents/ และจากภายนอก
sys.path.insert(0, os.path.dirname(__file__))

from agent_runner import (
    update_office,
    load_team_config,
    get_anthropic_client,
    get_openai_compatible_client,
    build_system_prompt,
)
from tools import registry


def run_agent_with_tools(
    agent_id: str,
    task: str,
    model: str = None,
    role: str = None,
    provider: str = None,
    base_url: str = None,
    tool_names: list[str] = None,
    max_turns: int = 10,
) -> str | None:
    """
    รัน agent พร้อม tool-use loop

    Args:
        agent_id:    ID ของ agent
        task:        งานที่ต้องทำ
        tool_names:  รายชื่อ tools ["all"] หรือ ["web_search", "read_file"]
                     None = อ่านจาก team.json (field "tools")
        max_turns:   จำนวนรอบสูงสุดของ tool loop
    """
    config = load_team_config()
    agent_config = config.get(agent_id, {})
    model    = model    or agent_config.get("model",    "claude-sonnet-4-6")
    role     = role     or agent_config.get("role",     "AI assistant")
    provider = provider or agent_config.get("provider", "anthropic")
    base_url = base_url or agent_config.get("base_url")
    system   = build_system_prompt(agent_id, role, agent_config)

    # อ่าน tools จาก config ถ้าไม่ได้ส่งมา
    if tool_names is None:
        tool_names = agent_config.get("tools", [])

    if not tool_names:
        update_office(agent_id, "error", "ไม่มี tools กำหนดไว้")
        return None

    available = registry.names()
    tools_used = [n for n in (available if "all" in tool_names else tool_names) if n in available]

    if not tools_used:
        update_office(agent_id, "error", f"ไม่พบ tools: {tool_names}")
        return None

    update_office(agent_id, "thinking", f"เตรียม tools: {', '.join(tools_used)}")

    if provider == "anthropic":
        return _loop_anthropic(agent_id, task, model, system, tools_used, max_turns, provider)
    else:
        return _loop_openai(agent_id, task, model, system, provider, base_url, tools_used, max_turns)


# ─── Anthropic tool-use loop ───

def _loop_anthropic(
    agent_id: str, task: str, model: str, system: str,
    tool_names: list[str], max_turns: int, provider: str,
) -> str | None:
    client = get_anthropic_client()
    schemas = registry.schemas("anthropic", tool_names)
    messages = [{"role": "user", "content": task}]

    for turn in range(1, max_turns + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=system,
                tools=schemas,
                messages=messages,
            )
        except Exception as e:
            update_office(agent_id, "error", f"API error: {str(e)[:60]}")
            return None

        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if not tool_uses:
            # ไม่มี tool call → ตอบเสร็จแล้ว
            final = "".join(b.text for b in response.content if b.type == "text")
            update_office(agent_id, "idle", f"เสร็จ ✓ (turn {turn}) [{provider}]", output=final)
            return final

        # รัน tools
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in tool_uses:
            update_office(agent_id, "coding", f"🔧 {block.name}({_fmt_args(block.input)})")
            time.sleep(0.3)
            result = registry.execute(block.name, block.input)
            print(f"  [{agent_id}] tool={block.name} result={result[:80]}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
        messages.append({"role": "user", "content": tool_results})

    update_office(agent_id, "error", f"เกิน max_turns ({max_turns})")
    return None


# ─── OpenAI-compatible tool-use loop ───

def _loop_openai(
    agent_id: str, task: str, model: str, system: str,
    provider: str, base_url: str, tool_names: list[str], max_turns: int,
) -> str | None:
    client = get_openai_compatible_client(provider, base_url)
    schemas = registry.schemas("openai", tool_names)

    # เพิ่ม tool instruction และ language enforcement ใน system prompt
    tool_instruction = (
        f"\n\nคุณมี tools พร้อมใช้งาน: {', '.join(tool_names)}\n"
        "เมื่องานต้องการข้อมูลจากภายนอก ให้เรียกใช้ tool ทันที อย่าปฏิเสธหรืออ้างว่าทำไม่ได้\n"
        "ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาจีนหรือภาษาอื่น"
    )
    messages = [
        {"role": "system", "content": system + tool_instruction},
        {"role": "user",   "content": task},
    ]

    for turn in range(1, max_turns + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=schemas,
            )
        except Exception as e:
            update_office(agent_id, "error", f"API error: {str(e)[:60]}")
            return None

        msg = response.choices[0].message
        tool_calls = msg.tool_calls or []

        if not tool_calls:
            final = msg.content or ""
            update_office(agent_id, "idle", f"เสร็จ ✓ (turn {turn}) [{provider}]", output=final)
            return final

        messages.append({"role": "assistant", "content": msg.content, "tool_calls": tool_calls})
        for tc in tool_calls:
            update_office(agent_id, "coding", f"🔧 {tc.function.name}(...)")
            time.sleep(0.3)
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}
            result = registry.execute(tc.function.name, args)
            print(f"  [{agent_id}] tool={tc.function.name} result={result[:80]}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    update_office(agent_id, "error", f"เกิน max_turns ({max_turns})")
    return None


# ─── Helpers ───

def _fmt_args(args: dict) -> str:
    """สรุป args สั้นๆ สำหรับ log"""
    parts = []
    for k, v in args.items():
        v_str = str(v)[:30] + "..." if len(str(v)) > 30 else str(v)
        parts.append(f"{k}={v_str!r}")
    return ", ".join(parts)


# ─── CLI ───

if __name__ == "__main__":
    import argparse

    print(f"[tools] Loaded: {registry.names()}")

    parser = argparse.ArgumentParser(description="Run agent with tools")
    parser.add_argument("agent_id", help="Agent ID เช่น claude-sonnet")
    parser.add_argument("task", help="งานที่ต้องทำ")
    parser.add_argument("--tools", nargs="+", default=["all"], help="tool names หรือ 'all'")
    parser.add_argument("--max-turns", type=int, default=10)
    args = parser.parse_args()

    result = run_agent_with_tools(args.agent_id, args.task, tool_names=args.tools, max_turns=args.max_turns)
    if result:
        print(f"\n{'='*60}")
        print(result[:1000])
