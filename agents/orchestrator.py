"""
Orchestrator — รัน multi-agent พร้อมกัน
"""

import json
import os
import threading
import time
from agent_runner import run_agent, run_agent_stream, update_office, load_team_config
from agent_tools import run_agent_with_tools

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def run_team(tasks: dict, stream: bool = False):
    """
    รัน agents ทั้งทีมพร้อมกัน

    Args:
        tasks: dict ของ {agent_id: task_description}
        stream: ใช้ streaming mode หรือไม่
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    config = load_team_config()
    results = {}
    errors = {}

    def worker(agent_id, task):
        agent_config = config.get(agent_id, {})
        model = agent_config.get("model", "claude-sonnet-4-6")
        role = agent_config.get("role", "AI assistant")

        try:
            tool_names = agent_config.get("tools", [])
            if tool_names:
                result = run_agent_with_tools(agent_id, task, model=model, role=role)
            elif stream:
                result = run_agent_stream(agent_id, task, model=model, role=role)
            else:
                result = run_agent(agent_id, task, model=model, role=role)

            if result:
                results[agent_id] = result
                # บันทึกผลลัพธ์เป็นไฟล์
                outfile = os.path.join(RESULTS_DIR, f"{agent_id}-result.md")
                with open(outfile, "w", encoding="utf-8") as f:
                    f.write(f"# {agent_id} — Result\n\n")
                    f.write(f"**Task:** {task}\n\n")
                    f.write(f"**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
                    f.write(result)
        except Exception as e:
            errors[agent_id] = str(e)
            update_office(agent_id, "error", str(e)[:60])

    # เริ่มทุกตัวพร้อมกัน
    print(f"\n{'='*60}")
    print(f"  Claude Agent Office — Starting {len(tasks)} agents")
    print(f"{'='*60}\n")

    threads = []
    for agent_id, task in tasks.items():
        print(f"  → [{agent_id}] {task[:50]}...")
        t = threading.Thread(target=worker, args=(agent_id, task))
        t.start()
        threads.append(t)
        time.sleep(0.2)  # stagger เล็กน้อยไม่ให้ชนกัน

    # รอทุกตัวเสร็จ
    for t in threads:
        t.join()

    # สรุปผล
    print(f"\n{'='*60}")
    print(f"  Results: {len(results)} done, {len(errors)} errors")
    print(f"{'='*60}")

    for agent_id, result in results.items():
        print(f"\n  ✓ [{agent_id}] {len(result)} chars → outputs/{agent_id}-result.md")

    for agent_id, err in errors.items():
        print(f"\n  ✗ [{agent_id}] {err}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-file", type=str, help="JSON file with tasks")
    parser.add_argument("--stream", action="store_true")
    args = parser.parse_args()

    if args.tasks_file:
        with open(args.tasks_file, "r") as f:
            tasks = json.load(f)
    else:
        tasks = {
            "claude-opus": "วิเคราะห์แนวโน้ม AI Agent ปี 2026",
            "claude-sonnet": "ออกแบบ database schema สำหรับ e-commerce",
            "claude-haiku": "สรุป 5 เทคนิค prompt engineering ที่ดีที่สุด",
            "claude-code": "เขียน Python script สำหรับ data validation",
        }

    run_team(tasks, stream=args.stream)
