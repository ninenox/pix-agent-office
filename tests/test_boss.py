"""
Tests for agents/boss.py — JSON parsing และ validation
"""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))

from boss import BOSS_SYSTEM
import boss as boss_module


# ─── BOSS_SYSTEM template ───

def test_boss_system_has_team_desc_placeholder():
    assert "{team_desc}" in BOSS_SYSTEM


def test_boss_system_has_json_format():
    assert "assignments" in BOSS_SYSTEM
    assert "agent_id" in BOSS_SYSTEM


# ─── _parse result validation (simulate analyze_task logic) ───

VALID_CONFIG = {
    "agent-a": {"model": "qwen2.5:7b", "role": "Researcher"},
    "agent-b": {"model": "qwen2.5:7b", "role": "Developer"},
}


def _filter_assignments(raw: dict, config: dict) -> list:
    """จำลอง logic filter assignments จาก analyze_task"""
    valid_ids = {k for k in config.keys() if k != "boss"}
    return [
        a for a in raw.get("assignments", [])
        if a.get("agent_id") in valid_ids and a.get("task")
    ]


def test_valid_assignments_pass_filter():
    raw = {
        "plan": "แบ่งงานให้ทีม",
        "assignments": [
            {"agent_id": "agent-a", "task": "วิจัย"},
            {"agent_id": "agent-b", "task": "พัฒนา"},
        ]
    }
    result = _filter_assignments(raw, VALID_CONFIG)
    assert len(result) == 2


def test_unknown_agent_id_filtered_out():
    raw = {
        "assignments": [
            {"agent_id": "ghost-agent", "task": "งาน"},
            {"agent_id": "agent-a", "task": "งานจริง"},
        ]
    }
    result = _filter_assignments(raw, VALID_CONFIG)
    assert len(result) == 1
    assert result[0]["agent_id"] == "agent-a"


def test_empty_task_filtered_out():
    raw = {
        "assignments": [
            {"agent_id": "agent-a", "task": ""},
            {"agent_id": "agent-b", "task": "มีงาน"},
        ]
    }
    result = _filter_assignments(raw, VALID_CONFIG)
    assert len(result) == 1


def test_boss_key_excluded_from_valid_ids():
    config_with_boss = {**VALID_CONFIG, "boss": {"model": "qwen2.5:7b"}}
    raw = {
        "assignments": [
            {"agent_id": "boss", "task": "งาน boss"},
            {"agent_id": "agent-a", "task": "งาน a"},
        ]
    }
    result = _filter_assignments(raw, config_with_boss)
    assert all(a["agent_id"] != "boss" for a in result)


def test_json_with_markdown_fences_parseable():
    """boss อาจ return JSON ห่อด้วย markdown fences"""
    import re
    raw_text = '```json\n{"plan": "test", "assignments": []}\n```'
    cleaned = re.sub(r"```(?:json)?|```", "", raw_text).strip()
    parsed = json.loads(cleaned)
    assert parsed["plan"] == "test"


def test_invalid_json_raises():
    import re
    raw_text = "ขอโทษ ฉันไม่สามารถตอบได้"
    cleaned = re.sub(r"```(?:json)?|```", "", raw_text).strip()
    with pytest.raises(json.JSONDecodeError):
        json.loads(cleaned)
