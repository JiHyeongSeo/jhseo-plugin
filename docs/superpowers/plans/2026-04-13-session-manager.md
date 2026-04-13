# Session Manager Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Claude Code 세션 목록을 프로젝트별 트리로 탐색하고, fzf로 검색·resume·삭제할 수 있는 플러그인 + 터미널 도구를 만든다.

**Architecture:** `session_manager.py` 하나가 `--claude-mode` 플래그에 따라 두 역할을 수행한다 — 터미널에서는 rich + fzf 인터랙티브 피커, Claude 슬래시 커맨드에서는 텍스트 출력. `~/.claude/projects/*/sessions-index.json`을 데이터 소스로 사용한다.

**Tech Stack:** Python 3.12, rich 14.x, fzf (시스템 설치), pytest, argparse

---

## File Map

| 파일 | 역할 |
|------|------|
| `plugins/session-manager/.claude-plugin/plugin.json` | 플러그인 메타데이터 |
| `plugins/session-manager/session_manager.py` | 핵심 로직 (터미널 + Claude 모드) |
| `plugins/session-manager/commands/sessions.md` | `/sessions` 슬래시 커맨드 정의 |
| `plugins/session-manager/SKILL.md` | 플러그인 문서 |
| `plugins/session-manager/tests/test_session_manager.py` | 단위 테스트 |
| `.claude-plugin/marketplace.json` | 마켓플레이스 등록 (기존 파일 수정) |

---

### Task 1: 플러그인 디렉터리 구조 + plugin.json

**Files:**
- Create: `plugins/session-manager/.claude-plugin/plugin.json`
- Create: `plugins/session-manager/commands/` (빈 디렉터리)
- Create: `plugins/session-manager/tests/` (빈 디렉터리)

- [ ] **Step 1: 디렉터리 생성**

```bash
mkdir -p plugins/session-manager/.claude-plugin
mkdir -p plugins/session-manager/commands
mkdir -p plugins/session-manager/tests
```

- [ ] **Step 2: plugin.json 작성**

`plugins/session-manager/.claude-plugin/plugin.json`:
```json
{
  "name": "session-manager",
  "description": "Claude Code 세션 브라우저. 프로젝트별 트리 탐색, fzf 검색, resume/삭제 관리",
  "version": "1.0.0",
  "author": {
    "name": "SOL Team"
  },
  "homepage": "https://gitlab.nexon.com/da_div/SOL/claude-plugins",
  "repository": "https://gitlab.nexon.com/da_div/SOL/claude-plugins.git",
  "keywords": [
    "session",
    "resume",
    "browser",
    "fzf",
    "세션",
    "세션관리"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add plugins/session-manager/
git commit -m "feat: session-manager 플러그인 스캐폴드"
```

---

### Task 2: 데이터 로딩 함수 (TDD)

**Files:**
- Create: `plugins/session-manager/session_manager.py`
- Create: `plugins/session-manager/tests/test_session_manager.py`

- [ ] **Step 1: 테스트 파일 작성 (`load_all_sessions`, `group_by_project`)**

`plugins/session-manager/tests/test_session_manager.py`:
```python
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
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
cd plugins/session-manager && python3 -m pytest tests/test_session_manager.py::TestLoadAllSessions tests/test_session_manager.py::TestGroupByProject -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError: No module named 'session_manager'`

- [ ] **Step 3: `session_manager.py` 뼈대 + 데이터 로딩 구현**

`plugins/session-manager/session_manager.py`:
```python
#!/usr/bin/env python3
"""claude-sessions: Claude Code session browser and manager"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"


def load_all_sessions() -> list[dict]:
    """~/.claude/projects/*/sessions-index.json 에서 모든 세션 엔트리를 읽어 반환."""
    sessions = []
    for index_file in PROJECTS_DIR.glob("*/sessions-index.json"):
        try:
            data = json.loads(index_file.read_text(encoding="utf-8"))
            sessions.extend(data.get("entries", []))
        except (json.JSONDecodeError, OSError):
            pass
    return sessions


def group_by_project(sessions: list[dict]) -> dict[str, list[dict]]:
    """sessions를 projectPath 기준으로 그룹화. 각 그룹은 modified 내림차순 정렬."""
    groups: dict[str, list[dict]] = {}
    for s in sessions:
        key = s.get("projectPath", "unknown")
        groups.setdefault(key, []).append(s)
    for key in groups:
        groups[key].sort(key=lambda x: x.get("modified", ""), reverse=True)
    return dict(sorted(groups.items()))
```

- [ ] **Step 4: 테스트 실행 (통과 확인)**

```bash
cd plugins/session-manager && python3 -m pytest tests/test_session_manager.py::TestLoadAllSessions tests/test_session_manager.py::TestGroupByProject -v
```

Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/tests/
git commit -m "feat: 세션 데이터 로딩 및 그룹화 구현 (TDD)"
```

---

### Task 3: 포맷팅 함수 (TDD)

**Files:**
- Modify: `plugins/session-manager/session_manager.py` (함수 추가)
- Modify: `plugins/session-manager/tests/test_session_manager.py` (테스트 추가)

- [ ] **Step 1: 테스트 추가 (`format_session_line`, `format_claude_output`, `format_stats`)**

`plugins/session-manager/tests/test_session_manager.py` 파일 끝에 추가:
```python
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
        # summary가 60자 이하로 잘림 — 전체 라인은 합리적인 길이
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
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
cd plugins/session-manager && python3 -m pytest tests/test_session_manager.py::TestFormatSessionLine tests/test_session_manager.py::TestFormatClaudeOutput tests/test_session_manager.py::TestFormatStats -v 2>&1 | head -20
```

Expected: `AttributeError: module 'session_manager' has no attribute 'format_session_line'`

- [ ] **Step 3: 포맷팅 함수 구현**

`plugins/session-manager/session_manager.py`에 추가 (파일 끝, `group_by_project` 아래):
```python
def format_session_line(session: dict) -> str:
    """세션을 fzf 입력용 한 줄 문자열로 변환. 마지막 토큰은 반드시 sessionId."""
    date = session.get("modified", "")[:10]
    project = session.get("projectPath", "?").split("/")[-1]
    summary = session.get("summary", session.get("firstPrompt", "No summary"))[:60]
    branch = session.get("gitBranch", "")
    msgs = session.get("messageCount", 0)
    session_id = session.get("sessionId", "")
    return f"{date}  {project:<20}  {summary:<60}  [{branch}] {msgs}msgs  {session_id}"


def format_claude_output(sessions: list[dict], filter_str: str = "") -> str:
    """Claude --claude-mode용 평문 텍스트 출력."""
    groups = group_by_project(sessions)
    lines = [f"## Claude Sessions (총 {len(sessions)}개, {len(groups)}개 프로젝트)\n"]
    for project_path, entries in groups.items():
        if filter_str and filter_str.lower() not in project_path.lower():
            continue
        lines.append(f"\n### {project_path} ({len(entries)}개)")
        for s in entries:
            date = s.get("modified", "")[:10]
            summary = s.get("summary", "No summary")[:60]
            branch = s.get("gitBranch", "")
            msgs = s.get("messageCount", 0)
            lines.append(f"- {date}  {summary}  [{branch}]  {msgs}msgs")
    return "\n".join(lines)


def format_stats(sessions: list[dict]) -> str:
    """전체 통계 요약 문자열 반환."""
    groups = group_by_project(sessions)
    oldest = min(sessions, key=lambda x: x.get("created", ""), default=None)
    most_active = max(groups.items(), key=lambda x: len(x[1]), default=(None, []))

    lines = [
        f"총 세션: {len(sessions)}개",
        f"총 프로젝트: {len(groups)}개",
    ]
    if oldest:
        lines.append(
            f"가장 오래된 세션: {oldest.get('created', '')[:10]}  {oldest.get('summary', '')[:40]}"
        )
    if most_active[0]:
        lines.append(
            f"가장 활발한 프로젝트: {most_active[0]} ({len(most_active[1])}개 세션)"
        )
    return "\n".join(lines)
```

- [ ] **Step 4: 테스트 실행 (통과 확인)**

```bash
cd plugins/session-manager && python3 -m pytest tests/test_session_manager.py::TestFormatSessionLine tests/test_session_manager.py::TestFormatClaudeOutput tests/test_session_manager.py::TestFormatStats -v
```

Expected: `16 passed`

- [ ] **Step 5: Commit**

```bash
git add plugins/session-manager/
git commit -m "feat: 세션 포맷팅 함수 구현 (TDD)"
```

---

### Task 4: 삭제/정리 함수 (TDD)

**Files:**
- Modify: `plugins/session-manager/session_manager.py`
- Modify: `plugins/session-manager/tests/test_session_manager.py`

- [ ] **Step 1: 테스트 추가 (`delete_session`, `filter_old_sessions`)**

`plugins/session-manager/tests/test_session_manager.py` 파일 끝에 추가:
```python
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
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
cd plugins/session-manager && python3 -m pytest tests/test_session_manager.py::TestDeleteSession tests/test_session_manager.py::TestFilterOldSessions -v 2>&1 | head -20
```

Expected: `AttributeError: module 'session_manager' has no attribute 'delete_session'`

- [ ] **Step 3: 삭제/정리 함수 구현**

`plugins/session-manager/session_manager.py`에 추가:
```python
def delete_session(session: dict) -> None:
    """세션 .jsonl 파일 삭제 + sessions-index.json에서 항목 제거."""
    full_path = Path(session.get("fullPath", ""))
    session_id = session.get("sessionId", "")

    # .jsonl 파일 삭제
    try:
        if full_path.exists():
            full_path.unlink()
    except OSError:
        pass

    # sessions-index.json 업데이트
    index_path = full_path.parent / "sessions-index.json"
    try:
        if index_path.exists():
            data = json.loads(index_path.read_text(encoding="utf-8"))
            data["entries"] = [
                e for e in data.get("entries", [])
                if e.get("sessionId") != session_id
            ]
            index_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
    except (json.JSONDecodeError, OSError):
        pass


def filter_old_sessions(sessions: list[dict], days: int = 30) -> list[dict]:
    """modified 기준으로 days일 이상 지난 세션 목록 반환."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = []
    for s in sessions:
        modified = s.get("modified", "")
        if not modified:
            continue
        try:
            dt = datetime.fromisoformat(modified.replace("Z", "+00:00"))
            if dt < cutoff:
                result.append(s)
        except ValueError:
            pass
    return result
```

- [ ] **Step 4: 테스트 실행 (통과 확인)**

```bash
cd plugins/session-manager && python3 -m pytest tests/test_session_manager.py -v
```

Expected: `전체 테스트 passed`

- [ ] **Step 5: Commit**

```bash
git add plugins/session-manager/
git commit -m "feat: 세션 삭제·정리 함수 구현 (TDD)"
```

---

### Task 5: rich 트리 출력 + CLI 진입점

**Files:**
- Modify: `plugins/session-manager/session_manager.py` (print_tree + main 추가)

- [ ] **Step 1: `print_tree` 함수 구현**

`plugins/session-manager/session_manager.py`에 추가:
```python
def print_tree(sessions: list[dict]) -> None:
    """rich를 사용해 프로젝트별 세션 트리를 출력."""
    try:
        from rich.console import Console
        from rich.tree import Tree
        use_rich = True
    except ImportError:
        use_rich = False

    groups = group_by_project(sessions)
    if not groups:
        if use_rich:
            from rich.console import Console
            Console().print("[dim]세션이 없습니다.[/dim]")
        else:
            print("세션이 없습니다.")
        return

    if use_rich:
        from rich.console import Console
        from rich.tree import Tree
        console = Console()
        for project_path, entries in groups.items():
            tree = Tree(
                f"[bold blue]{project_path}[/bold blue]  "
                f"[dim]({len(entries)}개)[/dim]"
            )
            for s in entries:
                date = s.get("modified", "")[:10]
                summary = s.get("summary", "No summary")[:50]
                branch = s.get("gitBranch", "")
                msgs = s.get("messageCount", 0)
                tree.add(
                    f"{date}  [green]{summary}[/green]  "
                    f"[yellow][{branch}][/yellow]  {msgs}msgs"
                )
            console.print(tree)
            console.print()
    else:
        # rich 없을 때 폴백
        for project_path, entries in groups.items():
            print(f"\n[{project_path}]  ({len(entries)}개)")
            for i, s in enumerate(entries):
                date = s.get("modified", "")[:10]
                summary = s.get("summary", "No summary")[:50]
                branch = s.get("gitBranch", "")
                msgs = s.get("messageCount", 0)
                prefix = "└─" if i == len(entries) - 1 else "├─"
                print(f"  {prefix} {date}  {summary}  [{branch}]  {msgs}msgs")
```

- [ ] **Step 2: `install_cli` 함수 구현**

`plugins/session-manager/session_manager.py`에 추가:
```python
def install_cli() -> None:
    """session_manager.py를 ~/.local/bin/claude-sessions 심링크로 설치."""
    script_path = Path(__file__).resolve()
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link_path = bin_dir / "claude-sessions"

    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    link_path.symlink_to(script_path)
    os.chmod(link_path, 0o755)

    path_dirs = os.environ.get("PATH", "").split(":")
    in_path = str(bin_dir) in path_dirs

    print(f"설치 완료: {link_path}")
    print(f"  -> {script_path}")
    if not in_path:
        print(f"\n주의: {bin_dir} 이 PATH에 없습니다.")
        print("다음을 ~/.bashrc 또는 ~/.zshrc에 추가하세요:")
        print(f'  export PATH="$HOME/.local/bin:$PATH"')
```

- [ ] **Step 3: `main` 함수 + argparse 구현**

`plugins/session-manager/session_manager.py`에 추가:
```python
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="claude-sessions",
        description="Claude Code 세션 브라우저",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="fzf 없이 rich 트리로 출력"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="전체 통계 요약 출력"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="30일 이상 지난 세션 인터랙티브 정리"
    )
    parser.add_argument(
        "--claude-mode", action="store_true",
        help="Claude 슬래시 커맨드용 평문 텍스트 출력"
    )
    parser.add_argument(
        "--filter", metavar="KEYWORD", default="",
        help="프로젝트 경로 필터 (--claude-mode, --list에서 사용)"
    )
    parser.add_argument(
        "action", nargs="?", default=None,
        help="install: ~/.local/bin/claude-sessions 심링크 설치"
    )

    args = parser.parse_args()
    sessions = load_all_sessions()

    if args.action == "install":
        install_cli()
        return

    if args.claude_mode:
        print(format_claude_output(sessions, filter_str=args.filter))
        return

    if args.stats:
        print(format_stats(sessions))
        return

    if args.list:
        if args.filter:
            sessions = [
                s for s in sessions
                if args.filter.lower() in s.get("projectPath", "").lower()
            ]
        print_tree(sessions)
        return

    if args.clean:
        old = filter_old_sessions(sessions, days=30)
        if not old:
            print("30일 이상 지난 세션이 없습니다.")
            return
        print(f"30일 이상 지난 세션 {len(old)}개:")
        for s in old:
            print(f"  {s.get('modified', '')[:10]}  {s.get('summary', '')[:50]}")
        confirm = input("\n모두 삭제하시겠습니까? (y/N) ").strip().lower()
        if confirm == "y":
            for s in old:
                delete_session(s)
            print(f"{len(old)}개 삭제 완료.")
        return

    # 기본: fzf 인터랙티브 모드
    if not shutil.which("fzf"):
        print("fzf가 설치되지 않았습니다. --list 모드로 전환합니다.")
        print("fzf 설치: sudo apt install fzf  또는  brew install fzf")
        print()
        print_tree(sessions)
        return

    selected = run_fzf(sessions)
    if selected:
        show_action_menu(selected)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 스모크 테스트 (--list 모드)**

```bash
cd plugins/session-manager && python3 session_manager.py --list 2>&1 | head -20
```

Expected: 프로젝트별 트리가 출력됨 (에러 없음)

- [ ] **Step 5: 스모크 테스트 (--stats 모드)**

```bash
cd plugins/session-manager && python3 session_manager.py --stats
```

Expected: `총 세션: N개` 형태의 통계 출력

- [ ] **Step 6: 스모크 테스트 (--claude-mode)**

```bash
cd plugins/session-manager && python3 session_manager.py --claude-mode 2>&1 | head -15
```

Expected: `## Claude Sessions (총 N개, M개 프로젝트)` 헤더로 시작하는 출력

- [ ] **Step 7: Commit**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: rich 트리 출력 + CLI 진입점 구현"
```

---

### Task 6: fzf 인터랙티브 모드 + 액션 메뉴

**Files:**
- Modify: `plugins/session-manager/session_manager.py` (`run_fzf`, `show_action_menu` 추가)

- [ ] **Step 1: `run_fzf` + `show_action_menu` 구현**

`plugins/session-manager/session_manager.py`에서 `main()` 위에 추가:
```python
def run_fzf(sessions: list[dict]) -> dict | None:
    """fzf로 세션 선택. 취소하면 None 반환."""
    lines = [format_session_line(s) for s in sessions]
    id_map = {s["sessionId"]: s for s in sessions}

    try:
        result = subprocess.run(
            [
                "fzf",
                "--ansi",
                "--height=60%",
                "--layout=reverse",
                "--border",
                "--prompt=세션 검색> ",
                "--header=Enter:선택  Ctrl-C:취소",
            ],
            input="\n".join(lines),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        selected_line = result.stdout.strip()
        if not selected_line:
            return None
        # 마지막 토큰이 sessionId
        session_id = selected_line.split()[-1]
        return id_map.get(session_id)
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return None


def show_action_menu(session: dict) -> None:
    """선택된 세션의 액션 메뉴를 표시하고 실행."""
    print()
    print(f"  세션: {session.get('summary', '')[:60]}")
    print(f"  프로젝트: {session.get('projectPath', '')}")
    print(f"  날짜: {session.get('modified', '')[:10]}")
    print(f"  ID: {session.get('sessionId', '')}")
    print()
    print("  r) Resume    d) Delete    v) View details    q) Quit")
    print()

    try:
        choice = input("  선택> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if choice == "r":
        project_path = session.get("projectPath", "")
        session_id = session.get("sessionId", "")
        cmd = f'cd "{project_path}" && claude resume {session_id}'
        print(f"\n실행: {cmd}\n")
        os.execlp("bash", "bash", "-c", cmd)

    elif choice == "d":
        try:
            confirm = input(
                f"  '{session.get('summary', '')[:40]}' 를 삭제하시겠습니까? (y/N) "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if confirm == "y":
            delete_session(session)
            print("  삭제 완료.")

    elif choice == "v":
        print()
        print(f"  Summary     : {session.get('summary', '')}")
        print(f"  First prompt: {session.get('firstPrompt', '')[:100]}")
        print(f"  Created     : {session.get('created', '')}")
        print(f"  Modified    : {session.get('modified', '')}")
        print(f"  Branch      : {session.get('gitBranch', '')}")
        print(f"  Messages    : {session.get('messageCount', 0)}")
        print(f"  Session ID  : {session.get('sessionId', '')}")
        print(f"  Project     : {session.get('projectPath', '')}")
```

- [ ] **Step 2: 스모크 테스트 — fzf 기본 모드**

```bash
cd plugins/session-manager && python3 session_manager.py
```

Expected: fzf 피커가 열리고, 세션 목록이 보임. 선택 후 r/d/v/q 메뉴 동작 확인.

- [ ] **Step 3: Commit**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: fzf 인터랙티브 피커 + 액션 메뉴 구현"
```

---

### Task 7: `/sessions` 슬래시 커맨드 정의

**Files:**
- Create: `plugins/session-manager/commands/sessions.md`

- [ ] **Step 1: `commands/sessions.md` 작성**

```markdown
---
description: Claude Code 세션 목록 조회 및 관리
---

# Claude 세션 관리

사용자 요청: $ARGUMENTS

## 동작 방식

`session_manager.py --claude-mode`를 실행하여 세션 목록을 텍스트로 출력합니다.

## 특수 액션

**install** 요청인 경우 (`$ARGUMENTS`가 "install"):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py install
```
설치 완료 후 결과를 사용자에게 알려주세요.

## 일반 조회

`$ARGUMENTS`를 다음 규칙으로 변환하여 실행:

| 요청 | 실행 |
|------|------|
| (없음) | `python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py --claude-mode` |
| `--stats` 또는 "통계" | `python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py --stats` |
| 프로젝트명 키워드 | `python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py --claude-mode --filter "키워드"` |

## 출력 후

- 세션 목록을 보여준 뒤, 사용자가 특정 세션 ID나 이름을 언급하면 `claude resume <sessionId>` 명령어를 안내합니다.
- 삭제 요청은 터미널에서 `claude-sessions` 도구를 사용하도록 안내합니다.
```

- [ ] **Step 2: 스모크 테스트 — Claude에서 `/sessions` 호출 시뮬레이션**

```bash
cd plugins/session-manager && CLAUDE_PLUGIN_ROOT="$(pwd)" python3 session_manager.py --claude-mode | head -20
```

Expected: `## Claude Sessions (총 N개, M개 프로젝트)` 로 시작하는 출력

- [ ] **Step 3: Commit**

```bash
git add plugins/session-manager/commands/sessions.md
git commit -m "feat: /sessions 슬래시 커맨드 정의"
```

---

### Task 8: SKILL.md + 마켓플레이스 등록

**Files:**
- Create: `plugins/session-manager/SKILL.md`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: `SKILL.md` 작성**

`plugins/session-manager/SKILL.md`:
```markdown
---
name: session-manager
description: Claude Code 세션 브라우저. 프로젝트별 트리 탐색, fzf 검색, resume/삭제 관리. "세션", "세션 목록", "sessions", "resume", "세션 관리" 키워드에서 활성화
---

# Session Manager

Claude Code 세션을 프로젝트별로 탐색하고 관리하는 플러그인입니다.

## 터미널 도구 설치

처음 한 번 Claude에서 실행:
```
/sessions install
```

## 터미널 사용법

```bash
claude-sessions           # fzf 인터랙티브 피커 (기본)
claude-sessions --list    # rich 트리 출력
claude-sessions --stats   # 통계 요약
claude-sessions --clean   # 30일 이상 지난 세션 정리
```

## Claude 슬래시 커맨드

```
/sessions                   # 전체 세션 목록
/sessions clean-chatbot     # 특정 프로젝트 필터
/sessions --stats           # 통계
/sessions install           # 터미널 도구 설치
```

## 의존성

- Python 3.10+
- `rich` (`pip install rich`)
- `fzf` (`sudo apt install fzf` 또는 `brew install fzf`)
```

- [ ] **Step 2: marketplace.json에 플러그인 등록**

`.claude-plugin/marketplace.json`의 `"plugins"` 배열 끝에 추가:
```json
{
  "name": "session-manager",
  "source": "./plugins/session-manager",
  "description": "Claude Code 세션 브라우저. 프로젝트별 트리 탐색, fzf 검색, resume/삭제 관리",
  "version": "1.0.0",
  "author": {
    "name": "SOL Team"
  },
  "keywords": ["session", "resume", "browser", "fzf", "세션", "세션관리"],
  "category": "productivity"
}
```

- [ ] **Step 3: 전체 테스트 재실행**

```bash
cd plugins/session-manager && python3 -m pytest tests/ -v
```

Expected: 전체 테스트 passed

- [ ] **Step 4: Commit**

```bash
git add plugins/session-manager/SKILL.md .claude-plugin/marketplace.json
git commit -m "feat: session-manager SKILL.md + 마켓플레이스 등록"
```

---

### Task 9: 최종 통합 검증

- [ ] **Step 1: 전체 테스트 통과 확인**

```bash
cd plugins/session-manager && python3 -m pytest tests/ -v --tb=short
```

Expected: 모든 테스트 passed, 에러 없음

- [ ] **Step 2: --list 스모크 테스트**

```bash
python3 plugins/session-manager/session_manager.py --list | head -30
```

Expected: 프로젝트별 트리 출력 확인

- [ ] **Step 3: --stats 스모크 테스트**

```bash
python3 plugins/session-manager/session_manager.py --stats
```

Expected: 세션 총 개수, 프로젝트 수, 가장 활발한 프로젝트 출력

- [ ] **Step 4: install 스모크 테스트**

```bash
python3 plugins/session-manager/session_manager.py install
ls -la ~/.local/bin/claude-sessions
```

Expected: 심링크 생성 확인

- [ ] **Step 5: 최종 커밋**

```bash
git add -A
git commit -m "feat: session-manager 플러그인 완성 v1.0.0"
```
