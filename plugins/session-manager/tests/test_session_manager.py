import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import session_manager


def make_session(
    session_id="abc-111",
    project="/home/user/project",
    summary="Test session",
    modified="2026-03-01T12:00:00.000Z",
    created="2026-03-01T10:00:00.000Z",
    branch="main",
    msgs=5,
    full_path=None,
):
    return {
        "sessionId": session_id,
        "projectPath": project,
        "summary": summary,
        "firstPrompt": "First prompt text",
        "modified": modified,
        "created": created,
        "gitBranch": branch,
        "messageCount": msgs,
        "fullPath": full_path or f"/tmp/{session_id}.jsonl",
        "isSidechain": False,
    }


class TestLoadAllSessions:
    def test_loads_sessions_from_index(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "PROJECTS_DIR", tmp_path)
        proj = tmp_path / "proj-a"
        proj.mkdir()
        entries = [make_session("s1"), make_session("s2")]
        (proj / "sessions-index.json").write_text(
            json.dumps({"version": 1, "entries": entries})
        )

        result = session_manager.load_all_sessions()

        assert len(result) == 2
        assert {s["sessionId"] for s in result} == {"s1", "s2"}

    def test_merges_multiple_projects(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "PROJECTS_DIR", tmp_path)
        for name in ("proj-a", "proj-b"):
            p = tmp_path / name
            p.mkdir()
            (p / "sessions-index.json").write_text(
                json.dumps({"version": 1, "entries": [make_session(name)]})
            )

        result = session_manager.load_all_sessions()

        assert len(result) == 2

    def test_skips_malformed_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "PROJECTS_DIR", tmp_path)
        bad = tmp_path / "bad"
        bad.mkdir()
        (bad / "sessions-index.json").write_text("not json {{")

        result = session_manager.load_all_sessions()

        assert result == []

    def test_skips_missing_entries_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "PROJECTS_DIR", tmp_path)
        p = tmp_path / "p"
        p.mkdir()
        (p / "sessions-index.json").write_text(json.dumps({"version": 1}))

        result = session_manager.load_all_sessions()

        assert result == []


class TestGroupByProject:
    def test_groups_by_project_path(self):
        sessions = [
            make_session("s1", project="/home/user/a"),
            make_session("s2", project="/home/user/b"),
            make_session("s3", project="/home/user/a"),
        ]

        groups = session_manager.group_by_project(sessions)

        assert len(groups["/home/user/a"]) == 2
        assert len(groups["/home/user/b"]) == 1

    def test_sorts_sessions_by_modified_desc(self):
        sessions = [
            make_session("s1", project="/home/user/a", modified="2026-01-01T00:00:00.000Z"),
            make_session("s2", project="/home/user/a", modified="2026-03-01T00:00:00.000Z"),
        ]

        groups = session_manager.group_by_project(sessions)

        # 최신 세션이 먼저
        assert groups["/home/user/a"][0]["sessionId"] == "s2"

    def test_sorts_projects_alphabetically(self):
        sessions = [
            make_session("s1", project="/home/user/z-project"),
            make_session("s2", project="/home/user/a-project"),
        ]

        groups = session_manager.group_by_project(sessions)

        assert list(groups.keys()) == ["/home/user/a-project", "/home/user/z-project"]

    def test_handles_missing_project_path(self):
        session = make_session("s1")
        session.pop("projectPath")

        groups = session_manager.group_by_project([session])

        assert "unknown" in groups
