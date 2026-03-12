"""
Agent Tools — Agent ที่ใช้ tools ได้ (web search, write file, etc.)
"""

import anthropic
import json
import os
import time
from agent_runner import update_office, load_team_config

client = anthropic.Anthropic(timeout=60.0)

# ─── Tool Definitions ───
TOOLS = [
    {
        "name": "web_search",
        "description": "ค้นหาข้อมูลบนเว็บ",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "คำค้นหา"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "write_file",
        "description": "เขียนไฟล์ผลลัพธ์",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "ชื่อไฟล์"},
                "content": {"type": "string", "description": "เนื้อหา"},
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "read_file",
        "description": "อ่านไฟล์",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "ชื่อไฟล์"},
            },
            "required": ["filename"],
        },
    },
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def execute_tool(name: str, input_data: dict) -> str:
    """รัน tool จริง — ใส่ logic ตามต้องการ"""
    if name == "web_search":
        # TODO: เชื่อมกับ search API จริง
        query = input_data.get("query", "")
        return f"[mock] ผลการค้นหา '{query}': ข้อมูลจำลองสำหรับ demo"

    elif name == "write_file":
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        safe_name = os.path.basename(input_data["filename"])
        filepath = os.path.join(OUTPUT_DIR, safe_name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(input_data["content"])
        return f"เขียนไฟล์ {safe_name} สำเร็จ ({len(input_data['content'])} chars)"

    elif name == "read_file":
        safe_name = os.path.basename(input_data["filename"])
        filepath = os.path.join(OUTPUT_DIR, safe_name)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()[:2000]
        except FileNotFoundError:
            return f"ไม่พบไฟล์ {safe_name}"

    return f"Unknown tool: {name}"


def run_agent_with_tools(agent_id: str, task: str, model: str = None, role: str = None, max_turns: int = 10):
    """
    รัน agent ที่ใช้ tools ได้ — วนลูปจนกว่า Claude จะตอบเสร็จ
    """
    if not model or not role:
        config = load_team_config()
        agent_config = config.get(agent_id, {})
        model = model or agent_config.get("model", "claude-sonnet-4-6")
        role = role or agent_config.get("role", "AI assistant")

    messages = [{"role": "user", "content": task}]
    update_office(agent_id, "thinking", "วิเคราะห์งาน...")

    for turn in range(max_turns):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=f"คุณคือ {role} ชื่อ {agent_id}",
                tools=TOOLS,
                messages=messages,
            )
        except Exception as e:
            update_office(agent_id, "error", f"API error: {str(e)[:50]}")
            return None

        # ตรวจสอบ tool_use blocks (รองรับหลาย tools พร้อมกัน)
        tool_results = []
        assistant_content = response.content

        for block in response.content:
            if block.type == "tool_use":
                update_office(agent_id, "coding", f"ใช้ {block.name}...")
                time.sleep(0.3)
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        if tool_results:
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})

        if not tool_results:
            # ตอบเสร็จแล้ว
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text

            update_office(agent_id, "idle", f"เสร็จแล้ว ✓ (turn {turn + 1})")
            return final_text

    update_office(agent_id, "error", "เกิน max turns")
    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("agent_id")
    parser.add_argument("task")
    args = parser.parse_args()

    result = run_agent_with_tools(args.agent_id, args.task)
    if result:
        print(f"\n{'='*60}")
        print(result[:500])
