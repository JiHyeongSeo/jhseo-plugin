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


class TestParseJsonlSession:
    def _make_jsonl(self, tmp_path, records: list[dict]) -> Path:
        f = tmp_path / "abc-123.jsonl"
        f.write_text("\n".join(json.dumps(r) for r in records))
        return f

    def test_extracts_project_path_from_cwd(self, tmp_path):
        jsonl = self._make_jsonl(tmp_path, [
            {"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:00.000Z", "sessionId": "abc-123", "cwd": "/home/user/myproject"},
            {"type": "user", "sessionId": "abc-123", "parentUuid": None, "message": {"role": "user", "content": [{"type": "text", "text": "Hello"}]}},
        ])
        result = session_manager.parse_jsonl_session(jsonl)
        assert result is not None
        assert result["projectPath"] == "/home/user/myproject"

    def test_extracts_ai_title_as_summary(self, tmp_path):
        jsonl = self._make_jsonl(tmp_path, [
            {"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:00.000Z", "sessionId": "abc-123", "cwd": "/home/user/proj"},
            {"type": "ai-title", "sessionId": "abc-123", "aiTitle": "Fix the login bug"},
        ])
        result = session_manager.parse_jsonl_session(jsonl)
        assert result is not None
        assert result["summary"] == "Fix the login bug"

    def test_falls_back_to_first_prompt_when_no_ai_title(self, tmp_path):
        jsonl = self._make_jsonl(tmp_path, [
            {"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:00.000Z", "sessionId": "abc-123", "cwd": "/home/user/proj"},
            {"type": "user", "sessionId": "abc-123", "parentUuid": None, "message": {"role": "user", "content": [{"type": "text", "text": "Please help me"}]}},
        ])
        result = session_manager.parse_jsonl_session(jsonl)
        assert result is not None
        assert "Please help me" in result["summary"]

    def test_counts_user_and_assistant_messages(self, tmp_path):
        jsonl = self._make_jsonl(tmp_path, [
            {"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:00.000Z", "sessionId": "abc-123", "cwd": "/home/user/proj"},
            {"type": "user", "sessionId": "abc-123", "parentUuid": None, "message": {"role": "user", "content": []}},
            {"type": "assistant", "sessionId": "abc-123", "message": {}},
            {"type": "user", "sessionId": "abc-123", "parentUuid": None, "message": {"role": "user", "content": []}},
        ])
        result = session_manager.parse_jsonl_session(jsonl)
        assert result is not None
        assert result["messageCount"] == 3

    def test_returns_none_if_no_cwd(self, tmp_path):
        jsonl = self._make_jsonl(tmp_path, [
            {"type": "queue-operation", "operation": "enqueue", "sessionId": "abc-123"},
        ])
        result = session_manager.parse_jsonl_session(jsonl)
        assert result is None

    def test_session_id_from_filename(self, tmp_path):
        jsonl = self._make_jsonl(tmp_path, [
            {"type": "queue-operation", "operation": "enqueue", "cwd": "/home/user/proj"},
        ])
        result = session_manager.parse_jsonl_session(jsonl)
        assert result is not None
        assert result["sessionId"] == "abc-123"


class TestLoadAllSessionsWithJsonl:
    def test_loads_from_jsonl_when_no_index(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "PROJECTS_DIR", tmp_path)
        proj = tmp_path / "proj-no-index"
        proj.mkdir()
        records = [
            {"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:00.000Z", "sessionId": "sess-1", "cwd": "/home/user/proj"},
            {"type": "user", "sessionId": "sess-1", "parentUuid": None, "message": {"role": "user", "content": [{"type": "text", "text": "Hi"}]}},
        ]
        (proj / "sess-1.jsonl").write_text("\n".join(json.dumps(r) for r in records))

        result = session_manager.load_all_sessions()

        assert len(result) == 1
        assert result[0]["sessionId"] == "sess-1"
        assert result[0]["projectPath"] == "/home/user/proj"

    def test_does_not_double_load_indexed_projects(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "PROJECTS_DIR", tmp_path)
        proj = tmp_path / "proj-with-index"
        proj.mkdir()
        entries = [make_session("s1")]
        (proj / "sessions-index.json").write_text(json.dumps({"version": 1, "entries": entries}))
        # .jsonl도 존재하지만 index가 있으므로 중복 로드 안 함
        (proj / "s1.jsonl").write_text('{"type":"queue-operation","cwd":"/x"}')

        result = session_manager.load_all_sessions()

        assert len(result) == 1
        assert result[0]["sessionId"] == "s1"


class TestGetAllPaneIds:
    def test_returns_pane_ids(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            class R:
                returncode = 0
                stdout = "%10\n%23\n%24\n"
            return R()
        monkeypatch.setattr(session_manager.subprocess, "run", fake_run)
        result = session_manager._get_all_pane_ids("claude-browser")
        assert result == {"%10", "%23", "%24"}

    def test_returns_empty_on_error(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            class R:
                returncode = 1
                stdout = ""
            return R()
        monkeypatch.setattr(session_manager.subprocess, "run", fake_run)
        result = session_manager._get_all_pane_ids("claude-browser")
        assert result == set()


class TestReadStateNewFormat:
    def test_default_has_slots_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        result = session_manager._read_state()
        assert "slots" in result
        assert result["slots"] == []
        assert result["background"] == []

    def test_reads_slots_format(self, tmp_path, monkeypatch):
        state_file = tmp_path / "state.json"
        state_file.write_text('{"slots": [{"session_id": "abc", "pane_id": "%23"}], "background": []}')
        monkeypatch.setattr(session_manager, "_STATE_FILE", state_file)
        result = session_manager._read_state()
        assert result["slots"][0]["session_id"] == "abc"
        assert result["slots"][0]["pane_id"] == "%23"


class TestGetTmuxOpenSessionsNewFormat:
    def _make_run(self, pane_ids="", window_names="", returncode=0):
        calls = []
        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            class R:
                pass
            r = R()
            r.returncode = returncode
            if "list-panes" in cmd:
                r.stdout = pane_ids
            else:
                r.stdout = window_names
            return r
        return fake_run, calls

    def test_returns_slot_ids_from_valid_panes(self, monkeypatch, tmp_path):
        state_file = tmp_path / "state.json"
        import json
        state_file.write_text(json.dumps({
            "slots": [
                {"session_id": "sess-a", "pane_id": "%23"},
                {"session_id": "sess-b", "pane_id": "%24"},
            ],
            "background": [],
        }))
        monkeypatch.setattr(session_manager, "_STATE_FILE", state_file)
        fake, _ = self._make_run(pane_ids="%10\n%23\n%24\n")
        monkeypatch.setattr(session_manager.subprocess, "run", fake)
        slot_ids, bg_ids = session_manager.get_tmux_open_sessions("claude-browser")
        assert slot_ids == {"sess-a", "sess-b"}
        assert bg_ids == set()

    def test_excludes_slot_with_missing_pane(self, monkeypatch, tmp_path):
        state_file = tmp_path / "state.json"
        import json
        state_file.write_text(json.dumps({
            "slots": [
                {"session_id": "sess-a", "pane_id": "%23"},
                {"session_id": "sess-b", "pane_id": "%99"},  # 없는 pane
            ],
            "background": [],
        }))
        monkeypatch.setattr(session_manager, "_STATE_FILE", state_file)
        fake, _ = self._make_run(pane_ids="%10\n%23\n")
        monkeypatch.setattr(session_manager.subprocess, "run", fake)
        slot_ids, bg_ids = session_manager.get_tmux_open_sessions("claude-browser")
        assert slot_ids == {"sess-a"}

    def test_returns_bg_sessions_from_windows(self, monkeypatch, tmp_path):
        state_file = tmp_path / "state.json"
        import json
        state_file.write_text(json.dumps({
            "slots": [],
            "background": ["sess-c"],
        }))
        monkeypatch.setattr(session_manager, "_STATE_FILE", state_file)
        fake, _ = self._make_run(pane_ids="%10\n", window_names="0 main\n1 sess-c\n")
        monkeypatch.setattr(session_manager.subprocess, "run", fake)
        slot_ids, bg_ids = session_manager.get_tmux_open_sessions("claude-browser")
        assert bg_ids == {"sess-c"}


class TestFormatSessionLineNewSignature:
    def test_green_when_in_slot_ids(self):
        s = make_session("abc-111")
        line = session_manager.format_session_line(s, slot_ids={"abc-111"})
        assert "\x1b[32m" in line  # 초록 ANSI

    def test_yellow_when_in_bg_ids(self):
        s = make_session("abc-222")
        line = session_manager.format_session_line(s, bg_ids={"abc-222"})
        assert "\x1b[33m" in line  # 노랑 ANSI

    def test_no_indicator_when_not_in_either(self):
        s = make_session("abc-333")
        line = session_manager.format_session_line(s, slot_ids={"other"}, bg_ids={"also-other"})
        assert "\x1b[32m" not in line
        assert "\x1b[33m" not in line

    def test_session_id_still_last_token(self):
        s = make_session("abc-444")
        line = session_manager.format_session_line(s, slot_ids={"abc-444"})
        import re
        plain = re.sub(r"\x1b\[[0-9;]*m", "", line)
        assert plain.split()[-1] == "abc-444"


class TestAskTargetSlot:
    def _make_slots(self):
        return [
            {"session_id": "sess-a", "pane_id": "%23"},
            {"session_id": "sess-b", "pane_id": "%24"},
        ]

    def _make_sessions(self):
        return [
            make_session("sess-a"),
            make_session("sess-b"),
        ]

    def test_returns_0_when_user_enters_1(self, monkeypatch):
        monkeypatch.setattr(session_manager, "_tty_input", lambda prompt: "1")
        result = session_manager._ask_target_slot(self._make_slots(), self._make_sessions())
        assert result == 0

    def test_returns_1_when_user_enters_2(self, monkeypatch):
        monkeypatch.setattr(session_manager, "_tty_input", lambda prompt: "2")
        result = session_manager._ask_target_slot(self._make_slots(), self._make_sessions())
        assert result == 1

    def test_returns_none_on_invalid_input(self, monkeypatch):
        monkeypatch.setattr(session_manager, "_tty_input", lambda prompt: "x")
        result = session_manager._ask_target_slot(self._make_slots(), self._make_sessions())
        assert result is None

    def test_returns_none_on_empty_input(self, monkeypatch):
        monkeypatch.setattr(session_manager, "_tty_input", lambda prompt: "")
        result = session_manager._ask_target_slot(self._make_slots(), self._make_sessions())
        assert result is None

    def test_returns_none_on_out_of_range(self, monkeypatch):
        monkeypatch.setattr(session_manager, "_tty_input", lambda prompt: "3")
        result = session_manager._ask_target_slot(self._make_slots(), self._make_sessions())
        assert result is None

    def test_prompt_contains_slot_summaries(self, monkeypatch):
        prompts = []
        monkeypatch.setattr(session_manager, "_tty_input", lambda p: prompts.append(p) or "")
        session_manager._ask_target_slot(self._make_slots(), self._make_sessions())
        assert len(prompts) == 1
        assert "위" in prompts[0]
        assert "아래" in prompts[0]
