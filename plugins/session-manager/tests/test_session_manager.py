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


class TestFormatSessionLine:
    def test_contains_session_id(self):
        s = make_session("abc-999")
        line = session_manager.format_session_line(s)
        assert "abc-999" in line

    def test_contains_summary(self):
        s = make_session(summary="My important session")
        line = session_manager.format_session_line(s)
        assert "My important session" in line

    def test_contains_branch(self):
        s = make_session(branch="feat/login")
        line = session_manager.format_session_line(s)
        assert "feat/login" in line

    def test_contains_message_count(self):
        s = make_session(msgs=42)
        line = session_manager.format_session_line(s)
        assert "42" in line

    def test_session_id_is_last_token(self):
        s = make_session("unique-id-xyz")
        line = session_manager.format_session_line(s)
        assert line.split()[-1] == "unique-id-xyz"

    def test_truncates_long_summary(self):
        s = make_session(summary="x" * 100)
        line = session_manager.format_session_line(s)
        assert len(line) < 300


class TestFormatClaudeOutput:
    def test_contains_project_path(self):
        sessions = [make_session("s1", project="/home/user/myproject")]
        output = session_manager.format_claude_output(sessions)
        assert "/home/user/myproject" in output

    def test_contains_summary(self):
        sessions = [make_session(summary="Important work done")]
        output = session_manager.format_claude_output(sessions)
        assert "Important work done" in output

    def test_total_count_in_header(self):
        sessions = [make_session("s1"), make_session("s2")]
        output = session_manager.format_claude_output(sessions)
        assert "2" in output

    def test_filter_excludes_other_projects(self):
        sessions = [
            make_session("s1", project="/home/user/project-a"),
            make_session("s2", project="/home/user/project-b"),
        ]
        output = session_manager.format_claude_output(sessions, filter_str="project-a")
        assert "project-a" in output
        assert "project-b" not in output

    def test_empty_filter_shows_all(self):
        sessions = [
            make_session("s1", project="/home/user/project-a"),
            make_session("s2", project="/home/user/project-b"),
        ]
        output = session_manager.format_claude_output(sessions, filter_str="")
        assert "project-a" in output
        assert "project-b" in output


class TestFormatStats:
    def test_shows_total_session_count(self):
        sessions = [make_session("s1"), make_session("s2"), make_session("s3")]
        stats = session_manager.format_stats(sessions)
        assert "3" in stats

    def test_shows_total_project_count(self):
        sessions = [
            make_session("s1", project="/home/user/a"),
            make_session("s2", project="/home/user/b"),
        ]
        stats = session_manager.format_stats(sessions)
        assert "2" in stats

    def test_empty_sessions(self):
        stats = session_manager.format_stats([])
        assert "0" in stats


class TestDeleteSession:
    def test_removes_jsonl_file(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        jsonl = proj / "s1.jsonl"
        jsonl.write_text("mock data")
        index = proj / "sessions-index.json"
        index.write_text(json.dumps({"version": 1, "entries": []}))

        session_manager.delete_session(make_session("s1", full_path=str(jsonl)))

        assert not jsonl.exists()

    def test_removes_entry_from_index(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        jsonl = proj / "s1.jsonl"
        jsonl.write_text("mock data")
        entries = [
            make_session("s1", full_path=str(jsonl)),
            make_session("s2", full_path=str(proj / "s2.jsonl")),
        ]
        index = proj / "sessions-index.json"
        index.write_text(json.dumps({"version": 1, "entries": entries}))

        session_manager.delete_session(entries[0])

        remaining = json.loads(index.read_text())["entries"]
        assert len(remaining) == 1
        assert remaining[0]["sessionId"] == "s2"

    def test_does_not_raise_if_jsonl_missing(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        index = proj / "sessions-index.json"
        index.write_text(json.dumps({"version": 1, "entries": []}))

        s = make_session("ghost", full_path=str(proj / "ghost.jsonl"))
        session_manager.delete_session(s)  # should not raise

    def test_does_not_raise_if_index_missing(self, tmp_path):
        jsonl = tmp_path / "s1.jsonl"
        jsonl.write_text("mock")
        s = make_session("s1", full_path=str(jsonl))
        session_manager.delete_session(s)  # should not raise
        assert not jsonl.exists()


class TestFilterOldSessions:
    def test_returns_sessions_older_than_days(self):
        from datetime import datetime, timezone, timedelta

        old = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
        new = datetime.now(timezone.utc).isoformat()
        sessions = [
            make_session("old", modified=old),
            make_session("new", modified=new),
        ]

        result = session_manager.filter_old_sessions(sessions, days=30)

        assert len(result) == 1
        assert result[0]["sessionId"] == "old"

    def test_returns_empty_if_all_recent(self):
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()
        sessions = [make_session("s1", modified=now)]

        result = session_manager.filter_old_sessions(sessions, days=30)

        assert result == []

    def test_skips_entries_with_no_modified(self):
        s = make_session("s1")
        s.pop("modified")

        result = session_manager.filter_old_sessions([s], days=30)

        assert result == []
