"""
Flask Backend — serve frontend + status API
"""

import json
import os
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
STATE_FILE = os.path.join(BASE_DIR, "state.json")

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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "time": time.strftime("%Y-%m-%d %H:%M:%S")})


if __name__ == "__main__":
    print(f"[server] Frontend: {FRONTEND_DIR}")
    print(f"[server] State: {STATE_FILE}")
    print(f"[server] Starting on http://0.0.0.0:19000")
    app.run(host="0.0.0.0", port=19000, debug=True)
