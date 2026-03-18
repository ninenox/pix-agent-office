"""
Tests for backend/app.py — Flask API endpoints
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))


@pytest.fixture
def client(tmp_path):
    """Flask test client พร้อม state.json ชั่วคราว"""
    import app as flask_app

    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({"agents": {}}), encoding="utf-8")
    flask_app.STATE_FILE = str(state_file)

    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


# ─── /health ───

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True


# ─── /status GET ───

def test_get_status_empty(client):
    res = client.get("/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "agents" in data


# ─── /status POST ───

def test_update_status(client):
    res = client.post("/status", json={
        "agent_id": "test-agent",
        "status": "coding",
        "detail": "กำลัง debug",
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["status"] == "coding"


def test_update_status_missing_agent_id(client):
    res = client.post("/status", json={"status": "idle"})
    assert res.status_code == 400


def test_update_status_no_body(client):
    res = client.post("/status")
    assert res.status_code in (400, 415)


# ─── /status/<agent_id> GET ───

def test_get_agent_status_not_found(client):
    res = client.get("/status/nonexistent")
    assert res.status_code == 404


def test_get_agent_status_found(client):
    client.post("/status", json={"agent_id": "bot-1", "status": "idle"})
    res = client.get("/status/bot-1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "idle"


# ─── /run POST ───

def test_run_missing_tasks(client):
    res = client.post("/run", json={})
    assert res.status_code == 400


def test_run_empty_tasks(client):
    res = client.post("/run", json={"tasks": {}})
    assert res.status_code == 400


def test_run_returns_started(client):
    res = client.post("/run", json={"tasks": {"agent-x": "ทดสอบ"}})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "agent-x" in data["started"]


# ─── /stop POST ───

def test_stop_all(client):
    client.post("/status", json={"agent_id": "a1", "status": "coding"})
    client.post("/status", json={"agent_id": "a2", "status": "writing"})
    res = client.post("/stop", json={})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "a1" in data["stopped"]
    assert "a2" in data["stopped"]


def test_stop_specific_agent(client):
    client.post("/status", json={"agent_id": "a1", "status": "coding"})
    client.post("/status", json={"agent_id": "a2", "status": "coding"})
    res = client.post("/stop", json={"agent_id": "a1"})
    data = res.get_json()
    assert "a1" in data["stopped"]
    assert "a2" not in data["stopped"]


def test_stop_idle_agent_not_in_stopped(client):
    client.post("/status", json={"agent_id": "idle-bot", "status": "idle"})
    res = client.post("/stop", json={"agent_id": "idle-bot"})
    data = res.get_json()
    assert "idle-bot" not in data["stopped"]


# ─── /team GET ───

def test_get_team(client):
    res = client.get("/team")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, dict)
