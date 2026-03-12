"""
Flask Backend — serve frontend + status API
"""

import json
import os
import sys
import threading
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
STATE_FILE = os.path.join(BASE_DIR, "state.json")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")

if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)


def read_state():
    """อ่าน state.json"""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"agents": {}}


def write_state(state):
    """เขียน state.json"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ─── Routes ───

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/status", methods=["GET"])
def get_status():
    """อ่านสถานะ agents ทั้งหมด"""
    state = read_state()
    return jsonify(state)


@app.route("/status", methods=["POST"])
def update_status():
    """อัพเดทสถานะ agent ตัวเดียว"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    agent_id = data.get("agent_id")
    status = data.get("status", "idle")
    detail = data.get("detail", "")

    if not agent_id:
        return jsonify({"error": "agent_id required"}), 400

    state = read_state()
    if "agents" not in state:
        state["agents"] = {}

    state["agents"][agent_id] = {
        "status": status,
        "detail": detail,
        "updated_at": time.strftime("%H:%M:%S"),
    }

    write_state(state)
    return jsonify({"ok": True, "agent_id": agent_id, "status": status})


@app.route("/status/<agent_id>", methods=["GET"])
def get_agent_status(agent_id):
    """อ่านสถานะ agent ตัวเดียว"""
    state = read_state()
    agent = state.get("agents", {}).get(agent_id)
    if agent:
        return jsonify({"agent_id": agent_id, **agent})
    return jsonify({"error": "agent not found"}), 404


@app.route("/run", methods=["POST"])
def run_agents():
    """รัน agents พร้อมกันในพื้นหลัง"""
    data = request.get_json()
    if not data or "tasks" not in data:
        return jsonify({"error": "tasks required"}), 400

    tasks = data["tasks"]
    if not isinstance(tasks, dict) or not tasks:
        return jsonify({"error": "tasks must be a non-empty object"}), 400

    def run_in_background():
        from orchestrator import run_team
        run_team(tasks)

    t = threading.Thread(target=run_in_background, daemon=True)
    t.start()

    return jsonify({"ok": True, "started": list(tasks.keys())})


@app.route("/brainstorm", methods=["POST"])
def brainstorm_route():
    """Boss วิเคราะห์งาน → แบ่งให้ทีม (Phase 1 sync, Phase 2 async)"""
    data = request.get_json()
    if not data or "task" not in data:
        return jsonify({"error": "task required"}), 400

    user_task = data["task"].strip()
    if not user_task:
        return jsonify({"error": "task cannot be empty"}), 400

    try:
        from boss import analyze_task
        plan = analyze_task(user_task)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Boss error: {e}"}), 500

    # Build tasks dict (assigned agents only)
    tasks = {a["agent_id"]: a["task"] for a in plan["assignments"]}
    assigned_ids = set(tasks.keys())

    # ตั้ง idle ให้ agent ที่ไม่ได้รับงาน
    from agent_runner import update_office, load_team_config
    config = load_team_config()
    for agent_id in config.keys():
        if agent_id not in assigned_ids:
            update_office(agent_id, "idle", "พักระหว่างรอทีม...")

    # รัน team ใน background
    def run_in_background():
        from orchestrator import run_team
        run_team(tasks)

    t = threading.Thread(target=run_in_background, daemon=True)
    t.start()

    return jsonify({
        "ok": True,
        "plan": plan.get("plan", ""),
        "assignments": plan["assignments"],
        "idle_agents": [a for a in config.keys() if a not in assigned_ids],
    })


@app.route("/stop", methods=["POST"])
def stop_agents():
    """หยุด agent และตั้งสถานะเป็น idle"""
    data = request.get_json() or {}
    agent_id = data.get("agent_id")  # None = หยุดทุกตัว

    state = read_state()
    if "agents" not in state:
        state["agents"] = {}

    stopped = []
    if agent_id:
        targets = [agent_id]
    else:
        targets = list(state["agents"].keys())

    for aid in targets:
        if state["agents"].get(aid, {}).get("status") not in ("idle", None):
            state["agents"][aid] = {
                "status": "idle",
                "detail": "หยุดโดยผู้ใช้",
                "updated_at": time.strftime("%H:%M:%S"),
            }
            stopped.append(aid)

    write_state(state)
    return jsonify({"ok": True, "stopped": stopped})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "time": time.strftime("%Y-%m-%d %H:%M:%S")})


if __name__ == "__main__":
    print(f"[server] Frontend: {FRONTEND_DIR}")
    print(f"[server] State: {STATE_FILE}")
    print(f"[server] Starting on http://0.0.0.0:19000")
    app.run(host="0.0.0.0", port=19000, debug=True)
