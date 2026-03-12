"""
Claude Agent Office — Main Entry Point
รัน Flask server + Agent orchestrator พร้อมกัน
"""

import threading
import argparse
import json
import os
import sys
import time
import shutil

_BASE = os.path.dirname(os.path.abspath(__file__))
for _p in [os.path.join(_BASE, "backend"), os.path.join(_BASE, "agents")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")
SAMPLE_FILE = os.path.join(os.path.dirname(__file__), "state.sample.json")
TEAM_CONFIG = os.path.join(os.path.dirname(__file__), "config", "team.json")


def init_state():
    """สร้าง state.json จาก template ถ้ายังไม่มี"""
    if not os.path.exists(STATE_FILE):
        shutil.copy(SAMPLE_FILE, STATE_FILE)
        print("[init] Created state.json from template")


def start_server():
    """เริ่ม Flask backend"""
    from app import app
    app.run(host="0.0.0.0", port=19000, debug=False)


def start_agents(task_file=None):
    """เริ่ม agent orchestrator"""
    from orchestrator import run_team

    if task_file:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    else:
        # Default demo tasks
        tasks = {
            "claude-opus": "วิเคราะห์แนวโน้ม AI ปี 2026",
            "claude-sonnet": "ออกแบบ REST API สำหรับ task management",
            "claude-haiku": "สรุปข่าวเทคโนโลยีวันนี้",
            "claude-code": "เขียน unit test สำหรับ user authentication",
        }

    run_team(tasks)


def main():
    parser = argparse.ArgumentParser(description="Claude Agent Office")
    parser.add_argument("--server-only", action="store_true", help="รัน Flask server อย่างเดียว")
    parser.add_argument("--agents-only", action="store_true", help="รัน agents อย่างเดียว")
    parser.add_argument("--tasks", type=str, help="ไฟล์ JSON กำหนด tasks")
    args = parser.parse_args()

    init_state()

    if args.server_only:
        print("[main] Starting server only...")
        start_server()
    elif args.agents_only:
        print("[main] Starting agents only...")
        start_agents(args.tasks)
    else:
        print("[main] Starting server + agents...")
        print("[main] Office UI → http://localhost:19000")

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        time.sleep(1)  # รอ server พร้อม
        start_agents(args.tasks)


if __name__ == "__main__":
    main()
