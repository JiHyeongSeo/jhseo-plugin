#!/usr/bin/env python3
"""claude-sessions: Claude Code session browser and manager"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

VERSION = "2.0.1"

PROJECTS_DIR = Path.home() / ".claude" / "projects"
TITLE_OVERRIDES_FILE = Path.home() / ".claude" / "session-manager-titles.json"


def parse_jsonl_session(jsonl_path: Path) -> dict | None:
    """sessions-index.json 없는 프로젝트의 .jsonl 파일에서 세션 메타데이터 추출."""
    try:
        lines = jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None

    session_id = jsonl_path.stem
    project_path = ""
    first_prompt = ""
    summary = ""
    created = ""
    msg_count = 0
    is_sidechain = False

    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        rtype = record.get("type", "")

        if not project_path and "cwd" in record:
            project_path = record["cwd"]

        if "sessionId" in record:
            session_id = record["sessionId"]

        if not created and rtype == "queue-operation" and record.get("operation") == "enqueue":
            created = record.get("timestamp", "")

        if rtype == "ai-title":
            summary = record.get("aiTitle", "")

        if not first_prompt and rtype == "user":
            content = record.get("message", {}).get("content", [])
            text = ""
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text = part.get("text", "")
                        break
            elif isinstance(content, str):
                text = content
            if "Caveat:" not in text[:100]:
                first_prompt = text[:200]
            if record.get("parentUuid") is not None:
                is_sidechain = True

        if rtype in ("user", "assistant"):
            msg_count += 1

    if not project_path:
        return None

    stat = jsonl_path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    if not created:
        created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()

    return {
        "sessionId": session_id,
        "fullPath": str(jsonl_path),
        "fileMtime": int(stat.st_mtime * 1000),
        "firstPrompt": first_prompt,
        "summary": summary or first_prompt[:60] or "No summary",
        "messageCount": msg_count,
        "created": created,
        "modified": modified,
        "gitBranch": "",
        "projectPath": project_path,
        "isSidechain": is_sidechain,
    }


def load_all_sessions() -> list[dict]:
    """~/.claude/projects/ 아래 모든 세션을 반환."""
    sessions = []
    indexed_ids: set[str] = set()

    for index_file in PROJECTS_DIR.glob("*/sessions-index.json"):
        try:
            data = json.loads(index_file.read_text(encoding="utf-8"))
            entries = data.get("entries", [])
            for entry in entries:
                sessions.append(entry)
                indexed_ids.add(entry.get("sessionId", ""))
        except (json.JSONDecodeError, OSError):
            pass

    # 인덱스에 없는 .jsonl도 직접 파싱 (새 세션이 인덱스에 반영되기 전에도 표시)
    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        for jsonl_file in proj_dir.glob("*.jsonl"):
            if jsonl_file.stem in indexed_ids:
                continue
            session = parse_jsonl_session(jsonl_file)
            if session:
                sessions.append(session)

    overrides = load_title_overrides()
    if overrides:
        for s in sessions:
            sid = s.get("sessionId", "")
            if sid in overrides:
                s["summary"] = overrides[sid]

    return sessions


def group_by_project(sessions: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for s in sessions:
        key = s.get("projectPath", "unknown")
        groups.setdefault(key, []).append(s)
    for key in groups:
        groups[key].sort(key=lambda x: x.get("modified", ""), reverse=True)
    return dict(sorted(groups.items()))


def _highlight_text(text: str, query: str) -> str:
    if not query:
        return text
    for term in query.split():
        if not term:
            continue
        try:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            text = pattern.sub(lambda m: f"\x1b[1;33m{m.group(0)}\x1b[0m", text)
        except re.error:
            pass
    return text


def clean_summary(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"<[^>]*$", "", text)
    text = " ".join(text.split())
    return text.strip()


def _tty_input(prompt: str) -> str:
    try:
        with open("/dev/tty", "r") as tty:
            sys.stderr.write("\033[2J\033[H" + prompt)
            sys.stderr.flush()
            return tty.readline().rstrip("\n")
    except (OSError, EOFError):
        return input(prompt)
    except KeyboardInterrupt:
        return ""


def load_title_overrides() -> dict[str, str]:
    try:
        return json.loads(TITLE_OVERRIDES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_title_override(session_id: str, title: str) -> None:
    overrides = load_title_overrides()
    overrides[session_id] = title
    TITLE_OVERRIDES_FILE.write_text(
        json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_display_summary(session: dict) -> str:
    raw = session.get("summary", "") or session.get("firstPrompt", "")
    cleaned = clean_summary(raw)
    if not cleaned or cleaned == "No summary":
        return "[제목 없음]"
    return cleaned


def get_search_content(session: dict) -> str:
    first_prompt = clean_summary(session.get("firstPrompt", ""))

    full_path = Path(session.get("fullPath", ""))
    if not full_path.exists():
        return first_prompt[:300]
    try:
        raw = full_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return first_prompt[:300]

    texts = []
    for line in raw.splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "user":
            continue
        content = record.get("message", {}).get("content", [])
        text = ""
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text", "")
                    break
        elif isinstance(content, str):
            text = content
        text = clean_summary(text)
        if not text or "Caveat:" in text[:50]:
            continue
        texts.append(text[:80])

    extra = " ".join(texts)
    if first_prompt:
        return f"{first_prompt[:150]} {extra}".strip()
    return extra


_STATE_FILE = Path("/tmp/claude-browser-state.json")


def _read_state() -> dict:
    try:
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"slots": [], "background": []}


def _write_state(state: dict) -> None:
    _STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def _get_all_pane_ids(tmux_session: str) -> set[str]:
    """window 0의 모든 pane ID 반환 (%숫자 형식)."""
    result = subprocess.run(
        ["tmux", "list-panes", "-t", f"{tmux_session}:0", "-F", "#{pane_id}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return set()
    return set(result.stdout.split())


def _get_fzf_pane_id(tmux_session: str) -> str:
    """fzf pane(window 0의 index 0 pane) ID 반환. 실패 시 세션:0.0 대체값."""
    result = subprocess.run(
        ["tmux", "list-panes", "-t", f"{tmux_session}:0",
         "-F", "#{pane_id} #{pane_index}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"{tmux_session}:0.0"
    for line in result.stdout.strip().split("\n"):
        parts = line.strip().split()
        if len(parts) == 2 and parts[1] == "0":
            return parts[0]
    return f"{tmux_session}:0.0"


def _find_bg_window_idx(session_id: str, tmux_session: str) -> str | None:
    """session_id와 이름이 일치하는 bg window index 반환. 없으면 None."""
    win_result = subprocess.run(
        ["tmux", "list-windows", "-t", tmux_session,
         "-F", "#{window_index} #{window_name}"],
        capture_output=True, text=True,
    )
    if win_result.returncode != 0:
        return None
    for line in win_result.stdout.strip().split("\n"):
        parts = line.strip().split(" ", 1)
        if len(parts) == 2 and parts[1] == session_id:
            return parts[0]
    return None


def _get_active_pane_id(tmux_session: str) -> str:
    """window 0의 현재 활성 pane ID 반환. split/join 직후 호출하면 새 pane ID를 반환."""
    r = subprocess.run(
        ["tmux", "display-message", "-t", f"{tmux_session}:0", "-p", "#{pane_id}"],
        capture_output=True, text=True,
    )
    return r.stdout.strip()


def get_tmux_open_sessions(tmux_session: str = "claude-browser") -> tuple[set[str], set[str]]:
    """상태 파일 + tmux 실제 상태로 열린 세션 목록 반환.

    Returns:
        (slot_session_ids, background_session_ids)
        slot_session_ids: 현재 pane에 열린 세션 (초록 표시)
        background_session_ids: bg window에 보존된 세션 (노랑 표시)
    """
    state = _read_state()
    slots: list[dict] = state.get("slots", [])
    bg_list: list[str] = state.get("background", [])

    all_pane_ids = _get_all_pane_ids(tmux_session)
    slot_ids = {
        slot["session_id"]
        for slot in slots
        if slot.get("pane_id", "") in all_pane_ids
    }

    bg_sessions: set[str] = set()
    if bg_list:
        win_result = subprocess.run(
            ["tmux", "list-windows", "-t", tmux_session, "-F", "#{window_name}"],
            capture_output=True, text=True,
        )
        if win_result.returncode == 0:
            window_names = set(win_result.stdout.split())
            bg_sessions = {s for s in bg_list if s in window_names}

    return slot_ids, bg_sessions


def format_session_line(
    session: dict,
    slot_ids: set[str] | None = None,
    bg_ids: set[str] | None = None,
) -> str:
    date = session.get("modified", "")[:10]
    project = session.get("projectPath", "?").split("/")[-1]
    summary = get_display_summary(session)[:60]
    branch = session.get("gitBranch", "")
    msgs = session.get("messageCount", 0)
    session_id = session.get("sessionId", "")

    if slot_ids and session_id in slot_ids:
        indicator = "\x1b[32m● \x1b[0m"
    elif bg_ids and session_id in bg_ids:
        indicator = "\x1b[33m● \x1b[0m"
    else:
        indicator = "  "

    display = f"{indicator}{date}  {project:<20}  {summary:<60}  [{branch}] {msgs}msgs"
    return f"{display}  {session_id}"


def filter_sessions_by_query(sessions: list[dict], query: str) -> list[dict]:
    """서버사이드 검색 필터: 메타데이터 + 대화 내용 모두 검색."""
    if not query.strip():
        return sessions
    terms = [t.lower() for t in query.split() if t]
    result = []
    for s in sessions:
        # 캐시에 _searchContent 있으면 사용, 없으면 직접 계산
        search_content = s.get("_searchContent") or get_search_content(s)
        search_text = " ".join([
            s.get("projectPath", ""),
            s.get("gitBranch", ""),
            get_display_summary(s),
            s.get("firstPrompt", ""),
            search_content,
        ]).lower()
        if all(term in search_text for term in terms):
            result.append(s)
    return result


def format_claude_output(sessions: list[dict], filter_str: str = "") -> str:
    groups = group_by_project(sessions)
    lines = [f"## Claude Sessions (총 {len(sessions)}개, {len(groups)}개 프로젝트)\n"]
    for project_path, entries in groups.items():
        if filter_str and filter_str.lower() not in project_path.lower():
            continue
        lines.append(f"\n### {project_path} ({len(entries)}개)")
        for s in entries:
            date = s.get("modified", "")[:10]
            summary = get_display_summary(s)[:60]
            branch = s.get("gitBranch", "")
            msgs = s.get("messageCount", 0)
            lines.append(f"- {date}  {summary}  [{branch}]  {msgs}msgs")
    return "\n".join(lines)


def format_stats(sessions: list[dict]) -> str:
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


def delete_session(session: dict) -> None:
    full_path = Path(session.get("fullPath", ""))
    session_id = session.get("sessionId", "")

    try:
        if full_path.exists():
            full_path.unlink()
    except OSError:
        pass

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


def print_tree(sessions: list[dict]) -> None:
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
                summary = get_display_summary(s)[:50]
                branch = s.get("gitBranch", "")
                msgs = s.get("messageCount", 0)
                tree.add(
                    f"{date}  [green]{summary}[/green]  "
                    f"[yellow][{branch}][/yellow]  {msgs}msgs"
                )
            console.print(tree)
            console.print()
    else:
        for project_path, entries in groups.items():
            print(f"\n[{project_path}]  ({len(entries)}개)")
            for i, s in enumerate(entries):
                date = s.get("modified", "")[:10]
                summary = get_display_summary(s)[:50]
                branch = s.get("gitBranch", "")
                msgs = s.get("messageCount", 0)
                prefix = "└─" if i == len(entries) - 1 else "├─"
                print(f"  {prefix} {date}  {summary}  [{branch}]  {msgs}msgs")


def _try_install_fzf() -> bool:
    import platform
    system = platform.system()
    if system == "Linux":
        if shutil.which("apt"):
            print("  → apt로 설치 중...")
            result = subprocess.run(["sudo", "apt", "install", "-y", "fzf"])
            if result.returncode == 0 and shutil.which("fzf"):
                print("  ✓ fzf 설치 완료")
                return True
    elif system == "Darwin":
        if shutil.which("brew"):
            print("  → brew로 설치 중...")
            result = subprocess.run(["brew", "install", "fzf"])
            if result.returncode == 0 and shutil.which("fzf"):
                print("  ✓ fzf 설치 완료")
                return True
    print("  ✗ 자동 설치 실패.")
    print("    Ubuntu/Debian : sudo apt install fzf")
    print("    macOS         : brew install fzf")
    return False


def _try_install_rich() -> bool:
    for pip_cmd in ("pip3", "pip"):
        if not shutil.which(pip_cmd):
            continue
        result = subprocess.run([pip_cmd, "install", "rich"])
        if result.returncode == 0:
            print("  ✓ rich 설치 완료")
            return True
    result = subprocess.run([sys.executable, "-m", "pip", "install", "rich"])
    if result.returncode == 0:
        print("  ✓ rich 설치 완료")
        return True
    print("  ✗ 자동 설치 실패. pip install rich")
    return False


def _check_and_install_deps() -> None:
    print("\n[의존성 확인]")
    if shutil.which("fzf"):
        fzf_ver = ""
        try:
            out = subprocess.run(["fzf", "--version"], capture_output=True, text=True)
            fzf_ver = out.stdout.strip().split()[0] if out.stdout else ""
        except OSError:
            pass
        print(f"  ✓ fzf {fzf_ver}")
    else:
        print("  ✗ fzf 없음 (필수)")
        _try_install_fzf()

    try:
        import importlib
        importlib.import_module("rich")
        print("  ✓ rich")
    except ImportError:
        print("  ✗ rich 없음 (선택: --list 트리 뷰)")
        _try_install_rich()


def install_cli() -> None:
    script_path = Path(__file__).resolve()
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link_path = bin_dir / "cs"

    old_link = bin_dir / "claude-sessions"
    if old_link.exists() or old_link.is_symlink():
        old_link.unlink()

    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    link_path.symlink_to(script_path)
    os.chmod(link_path, 0o755)

    print(f"\n[설치 완료]")
    print(f"  {link_path} -> {script_path}")

    path_dirs = os.environ.get("PATH", "").split(":")
    if str(bin_dir) not in path_dirs:
        print(f"\n  주의: {bin_dir} 이 PATH에 없습니다.")
        print(f'  ~/.zshrc 또는 ~/.bashrc에 추가: export PATH="$HOME/.local/bin:$PATH"')

    _check_and_install_deps()


def format_session_preview(session: dict, highlight: str = "") -> str:
    query = highlight.strip()
    query_terms = [t for t in query.split() if t] if query else []

    full_path = Path(session.get("fullPath", ""))
    header = [
        f"프로젝트: {session.get('projectPath', '')}",
        f"날짜:     {session.get('modified', '')[:10]}  |  메시지: {session.get('messageCount', 0)}개",
        f"제목:     {get_display_summary(session)}",
        "─" * 60,
    ]
    if query:
        header = [_highlight_text(line, query) for line in header]

    if not full_path.exists():
        return "\n".join(header + ["[세션 파일 없음]"])

    matched_msgs = []
    other_msgs = []

    SKILL_PATTERNS = (
        "Base directory for this skill:",
        "REQUIRED SUB-SKILL:",
        "subagent_type",
    )

    try:
        raw = full_path.read_text(encoding="utf-8", errors="replace")
        for line in raw.splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            rtype = record.get("type", "")
            if rtype not in ("user", "assistant"):
                continue

            content = record.get("message", {}).get("content", [])
            text = ""
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text = part.get("text", "")
                        break
            elif isinstance(content, str):
                text = content

            text = clean_summary(text)
            if not text or "Caveat:" in text[:50]:
                continue
            if any(pat in text for pat in SKILL_PATTERNS):
                continue

            prefix = "👤" if rtype == "user" else "🤖"
            msg_text = text[:300]

            if query_terms:
                text_lower = msg_text.lower()
                has_match = any(t.lower() in text_lower for t in query_terms)
                highlighted = _highlight_text(msg_text, query)
                entry = f"\n{prefix} {highlighted}"
                if has_match:
                    matched_msgs.append(entry)
                else:
                    other_msgs.append(entry)
            else:
                other_msgs.append(f"\n{prefix} {msg_text}")

    except OSError:
        other_msgs.append("[파일 읽기 오류]")

    if query_terms and matched_msgs:
        sep = [f"\n\x1b[1;33m── 검색어 '{query}' 포함 메시지 ({len(matched_msgs)}개) ──\x1b[0m"]
        messages = sep + matched_msgs
        if other_msgs:
            messages += ["\n\x1b[90m── 나머지 메시지 ──\x1b[0m"] + other_msgs[:20]
    else:
        messages = other_msgs

    return "\n".join(header + messages)


# ─── tmux 통합: 왼쪽 fzf 브라우저 + Enter시 오른쪽 분할 ─────────────────────

def _ask_target_slot(slots: list[dict], sessions: list[dict]) -> int | None:
    """슬롯 선택 프롬프트. 선택된 슬롯 인덱스(0 or 1) 반환, 취소/잘못된 입력은 None."""
    labels = ["위", "아래"]
    lines = ["\n  어느 슬롯에 열까요?\n"]
    for i, slot in enumerate(slots[:2]):
        sid = slot["session_id"]
        session = next((s for s in sessions if s.get("sessionId") == sid), None)
        project = (session.get("projectPath", "?").split("/")[-1] if session else "?")[:15]
        summary = get_display_summary(session)[:35] if session else sid[:20]
        lines.append(f"  {i + 1}) {labels[i]:<4} │ {project} — {summary}")
    lines.append(f"\n  선택 (1/{len(slots[:2])}): ")
    prompt = "\n".join(lines)
    try:
        choice = _tty_input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        return None
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(slots):
            return idx
    except ValueError:
        pass
    return None


def _get_right_width(tmux_session: str) -> int:
    """tmux 윈도우 너비의 60%를 절대값으로 반환."""
    w_result = subprocess.run(
        ["tmux", "display-message", "-t", f"{tmux_session}:0", "-p", "#{window_width}"],
        capture_output=True, text=True,
    )
    try:
        return max(60, int(int(w_result.stdout.strip()) * 0.70))
    except ValueError:
        return 130


def tmux_split_open(session_id: str, sessions_cache_path: str) -> None:
    """Enter: 선택한 세션을 슬롯에서 실행.

    슬롯 0개: 슬롯 1 생성 (수평 분할)
    슬롯 1개: 슬롯 1 교체 (기존 → background)
    슬롯 2개: 1/2 텍스트 프롬프트 → 선택 슬롯 교체
    이미 열린 세션: 해당 슬롯으로 포커스 이동
    """
    sessions: list[dict] = []
    if sessions_cache_path:
        try:
            sessions = json.loads(Path(sessions_cache_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if not sessions:
        sessions = load_all_sessions()

    session = next((s for s in sessions if s.get("sessionId") == session_id), None)
    if not session:
        return

    project_path = session.get("projectPath", "")
    tmux_session = "claude-browser"
    work_dir = project_path if project_path and Path(project_path).is_dir() else str(Path.home())

    state = _read_state()
    bg_list: list[str] = state.get("background", [])

    # 죽은 pane 자동 정리 (외부에서 Ctrl+C 등으로 pane이 종료된 경우)
    live_pane_ids = _get_all_pane_ids(tmux_session)
    slots: list[dict] = [s for s in state.get("slots", []) if s.get("pane_id", "") in live_pane_ids]
    if slots != state.get("slots", []):
        _write_state({"slots": slots, "background": bg_list})

    # 이미 슬롯에 열린 세션이면 포커스만 이동
    for slot in slots:
        if slot["session_id"] == session_id:
            subprocess.run(["tmux", "select-pane", "-t", slot["pane_id"]])
            return

    # 슬롯 2개 → 선택 프롬프트
    target_idx = 0
    if len(slots) == 2:
        chosen = _ask_target_slot(slots, sessions)
        if chosen is None:
            return
        target_idx = chosen

    # 타겟 슬롯의 기존 pane을 bg window로 보존
    old_session_id = ""
    if target_idx < len(slots):
        old_slot = slots[target_idx]
        old_pane_id = old_slot["pane_id"]
        old_session_id = old_slot["session_id"]
        subprocess.run([
            "tmux", "break-pane", "-d",
            "-s", old_pane_id,
            "-n", old_session_id,
        ])
        # break-pane 실패 검증 — 여전히 존재하면 kill
        if old_pane_id in _get_all_pane_ids(tmux_session):
            subprocess.run(["tmux", "kill-pane", "-t", old_pane_id], capture_output=True)
            old_session_id = ""  # bg 등록 취소
        slots.pop(target_idx)

    # bg 목록 갱신
    if old_session_id and old_session_id not in bg_list:
        bg_list.append(old_session_id)
    bg_list = [s for s in bg_list if s != session_id]

    # 대상 세션이 bg window에 있는지 확인
    bg_window_idx = _find_bg_window_idx(session_id, tmux_session)
    right_width = _get_right_width(tmux_session)

    # 새 pane 생성 위치 결정 및 실행
    new_pane_id = ""
    if len(slots) == 0:
        # 오른쪽에 슬롯 없음 → fzf 기준 수평 분할
        fzf_pane = _get_fzf_pane_id(tmux_session)
        if bg_window_idx is not None:
            subprocess.run([
                "tmux", "join-pane", "-h",
                "-s", f"{tmux_session}:{bg_window_idx}",
                "-t", fzf_pane,
            ])
            new_pane_id = _get_active_pane_id(tmux_session)
            if new_pane_id:
                subprocess.run(["tmux", "resize-pane", "-t", new_pane_id, "-x", str(right_width)])
        else:
            subprocess.run([
                "tmux", "split-window", "-h", "-l", str(right_width),
                "-t", fzf_pane, "-c", work_dir,
                f"claude --resume {session_id}",
            ])
            new_pane_id = _get_active_pane_id(tmux_session)

    elif target_idx == 0:
        # 위 슬롯 위치 → 남은 아래 슬롯(%ref) 위에 삽입
        ref_pane_id = slots[0]["pane_id"]
        if bg_window_idx is not None:
            subprocess.run([
                "tmux", "join-pane", "-v", "-b",
                "-s", f"{tmux_session}:{bg_window_idx}",
                "-t", ref_pane_id,
            ])
        else:
            subprocess.run([
                "tmux", "split-window", "-v", "-b",
                "-t", ref_pane_id, "-c", work_dir,
                f"claude --resume {session_id}",
            ])
        new_pane_id = _get_active_pane_id(tmux_session)

    else:
        # 아래 슬롯 위치 → 남은 위 슬롯(%ref) 아래에 삽입
        ref_pane_id = slots[0]["pane_id"]
        if bg_window_idx is not None:
            subprocess.run([
                "tmux", "join-pane", "-v",
                "-s", f"{tmux_session}:{bg_window_idx}",
                "-t", ref_pane_id,
            ])
        else:
            subprocess.run([
                "tmux", "split-window", "-v",
                "-t", ref_pane_id, "-c", work_dir,
                f"claude --resume {session_id}",
            ])
        new_pane_id = _get_active_pane_id(tmux_session)

    if not new_pane_id:
        return

    # slots에 새 슬롯 삽입 (위치 유지)
    slots.insert(target_idx, {"session_id": session_id, "pane_id": new_pane_id})
    _write_state({"slots": slots, "background": bg_list})
    subprocess.run(["tmux", "select-pane", "-t", new_pane_id])


def tmux_split_add(session_id: str, sessions_cache_path: str) -> None:
    """Ctrl+S: 슬롯 2 생성. 슬롯이 1개일 때만 동작.

    슬롯 0개 또는 2개: 무시
    이미 슬롯에 열린 세션: 해당 슬롯 포커스
    """
    sessions: list[dict] = []
    if sessions_cache_path:
        try:
            sessions = json.loads(Path(sessions_cache_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if not sessions:
        sessions = load_all_sessions()

    session = next((s for s in sessions if s.get("sessionId") == session_id), None)
    if not session:
        return

    project_path = session.get("projectPath", "")
    tmux_session = "claude-browser"
    work_dir = project_path if project_path and Path(project_path).is_dir() else str(Path.home())

    state = _read_state()
    bg_list: list[str] = state.get("background", [])

    # 죽은 pane 자동 정리
    live_pane_ids = _get_all_pane_ids(tmux_session)
    slots: list[dict] = [s for s in state.get("slots", []) if s.get("pane_id", "") in live_pane_ids]
    if slots != state.get("slots", []):
        _write_state({"slots": slots, "background": bg_list})

    # 슬롯 1개일 때만 동작
    if len(slots) != 1:
        return

    # 이미 슬롯에 열린 세션이면 포커스만
    for slot in slots:
        if slot["session_id"] == session_id:
            subprocess.run(["tmux", "select-pane", "-t", slot["pane_id"]])
            return

    bg_list_new = [s for s in bg_list if s != session_id]
    bg_window_idx = _find_bg_window_idx(session_id, tmux_session)
    slot0_pane_id = slots[0]["pane_id"]

    if bg_window_idx is not None:
        subprocess.run([
            "tmux", "join-pane", "-v",
            "-s", f"{tmux_session}:{bg_window_idx}",
            "-t", slot0_pane_id,
        ])
    else:
        subprocess.run([
            "tmux", "split-window", "-v",
            "-t", slot0_pane_id, "-c", work_dir,
            f"claude --resume {session_id}",
        ])

    new_pane_id = _get_active_pane_id(tmux_session)
    if not new_pane_id:
        return

    slots.append({"session_id": session_id, "pane_id": new_pane_id})
    _write_state({"slots": slots, "background": bg_list_new})
    subprocess.run(["tmux", "select-pane", "-t", new_pane_id])


def tmux_new_session(sessions_cache_path: str) -> None:
    """Ctrl+N: 디렉터리를 선택해 새 Claude 세션 시작 (--resume 없이)."""
    sessions: list[dict] = []
    if sessions_cache_path:
        try:
            sessions = json.loads(Path(sessions_cache_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if not sessions:
        sessions = load_all_sessions()

    # 기존 세션 프로젝트 경로 (존재하는 것만, 우선 표시)
    session_dirs = sorted({
        s.get("projectPath", "")
        for s in sessions
        if s.get("projectPath") and Path(s.get("projectPath", "")).is_dir()
    })

    # home 아래 숨김 폴더 제외 3단계까지 탐색
    try:
        find_result = subprocess.run(
            ["find", str(Path.home()), "-maxdepth", "3", "-type", "d",
             "!", "-path", "*/.*",
             "!", "-path", "*/node_modules/*",
             "!", "-path", "*/__pycache__/*"],
            capture_output=True, text=True, timeout=5,
        )
        find_dirs = [d for d in find_result.stdout.strip().split("\n") if d]
    except subprocess.TimeoutExpired:
        find_dirs = []

    seen: set[str] = set(session_dirs)
    all_dirs = list(session_dirs)
    for d in find_dirs:
        if d not in seen:
            seen.add(d)
            all_dirs.append(d)

    if not all_dirs:
        all_dirs = [str(Path.home())]

    fzf_result = subprocess.run(
        ["fzf",
         "--prompt", "새 세션 경로 선택: ",
         "--height", "80%", "--reverse", "--border",
         "--header", "Enter:선택  Esc:취소"],
        input="\n".join(all_dirs),
        capture_output=True, text=True,
    )
    if fzf_result.returncode != 0:
        return
    selected_dir = fzf_result.stdout.strip()
    if not selected_dir or not Path(selected_dir).is_dir():
        return

    tmux_session = "claude-browser"
    state = _read_state()
    bg_list: list[str] = state.get("background", [])
    right_width = _get_right_width(tmux_session)

    # 죽은 pane 자동 정리
    live_pane_ids = _get_all_pane_ids(tmux_session)
    slots: list[dict] = [s for s in state.get("slots", []) if s.get("pane_id", "") in live_pane_ids]
    if slots != state.get("slots", []):
        _write_state({"slots": slots, "background": bg_list})

    target_idx = 0
    if len(slots) == 2:
        chosen = _ask_target_slot(slots, sessions)
        if chosen is None:
            return
        target_idx = chosen

    old_session_id = ""
    if target_idx < len(slots):
        old_slot = slots[target_idx]
        old_pane_id = old_slot["pane_id"]
        old_session_id = old_slot["session_id"]
        subprocess.run([
            "tmux", "break-pane", "-d",
            "-s", old_pane_id,
            "-n", old_session_id,
        ])
        if old_pane_id in _get_all_pane_ids(tmux_session):
            subprocess.run(["tmux", "kill-pane", "-t", old_pane_id], capture_output=True)
            old_session_id = ""
        slots.pop(target_idx)

    if old_session_id and old_session_id not in bg_list:
        bg_list.append(old_session_id)

    if len(slots) == 0:
        fzf_pane = _get_fzf_pane_id(tmux_session)
        subprocess.run([
            "tmux", "split-window", "-h", "-l", str(right_width),
            "-t", fzf_pane, "-c", selected_dir,
            "claude",
        ])
    elif target_idx == 0:
        ref_pane_id = slots[0]["pane_id"]
        subprocess.run([
            "tmux", "split-window", "-v", "-b",
            "-t", ref_pane_id, "-c", selected_dir,
            "claude",
        ])
    else:
        ref_pane_id = slots[0]["pane_id"]
        subprocess.run([
            "tmux", "split-window", "-v",
            "-t", ref_pane_id, "-c", selected_dir,
            "claude",
        ])

    new_pane_id = _get_active_pane_id(tmux_session)
    if not new_pane_id:
        return

    # session_id는 빈 문자열 — claude 시작 후 자체적으로 세션 생성
    slots.insert(target_idx, {"session_id": "", "pane_id": new_pane_id})
    _write_state({"slots": slots, "background": bg_list})
    subprocess.run(["tmux", "select-pane", "-t", new_pane_id])


def run_fzf_tmux(cache_file: str, query_file: str) -> None:
    """tmux 세션 안의 왼쪽 pane에서 실행되는 fzf 브라우저.

    fzf --disabled: 클라이언트 필터링 OFF, Python 서버사이드 필터링 사용.
    검색어 → query_file 저장 → --fzf-list-lines reload → 메타데이터+대화 내용 검색.
    """
    tmux_session = "claude-browser"
    sessions = load_all_sessions()
    sessions = sorted(sessions, key=lambda s: s.get("modified", ""), reverse=True)
    slot_ids, bg_ids = get_tmux_open_sessions()

    # 시작 시 _searchContent 미리 계산 (reload 시 캐시에서 재사용)
    for s in sessions:
        s["_searchContent"] = get_search_content(s)

    lines = [format_session_line(s, slot_ids=slot_ids, bg_ids=bg_ids) for s in sessions]
    script_path = Path(__file__).resolve()

    if cache_file:
        try:
            Path(cache_file).write_text(
                json.dumps(sessions, ensure_ascii=False), encoding="utf-8"
            )
        except OSError:
            pass

    header = (
        "Enter:세션열기  Ctrl-S:화면분할  Ctrl-N:새세션  Ctrl-P:미리보기토글  Ctrl-D:삭제  Ctrl-T:제목편집\n"
        "Ctrl-R:날짜정렬  Ctrl-O:프로젝트정렬  Ctrl-Z:백그라운드(detach)  Ctrl-Q:완전종료"
    )

    # reload 공통 접두어: 현재 query를 파일에 저장 후 서버사이드 필터링
    _reload_with_cache = (
        f"printf '%s' {{q}} > {query_file}; "
        f"python3 {script_path} --fzf-list-lines --sessions-cache {cache_file} --query-file {query_file}"
    )
    # delete/edit-title 후 reload: cache stale 가능성 → 파일에서 새로 로드
    _reload_fresh = (
        f"printf '%s' {{q}} > {query_file}; "
        f"python3 {script_path} --fzf-list-lines --query-file {query_file}"
    )

    subprocess.run(
        [
            "fzf",
            "--ansi", "--disabled", "--no-sort", "--layout=reverse", "--border",
            "--prompt=세션 검색> ",
            f"--header={header}",
            "--color=hl:#ffaf00,hl+:#ffaf00",
            f"--preview=python3 {script_path} --preview-id {{-1}} --sessions-cache {cache_file} --query-file {query_file}",
            "--preview-window=bottom:40%:wrap",
            # 검색어 변경 → query 파일 기록 + 서버사이드 필터 reload + preview 갱신
            f"--bind=change:reload({_reload_with_cache})+refresh-preview",
            # 시작 시 green/yellow 점 동기화
            f"--bind=start:reload(python3 {script_path} --fzf-list-lines --sessions-cache {cache_file})",
            # Enter: 세션 열고 목록 reload (query 보존)
            (
                f"--bind=enter:execute("
                f"python3 {script_path} --tmux-split-open {{-1}}"
                f" --sessions-cache {cache_file})"
                f"+reload({_reload_with_cache})"
            ),
            # ctrl-s: 슬롯 2 추가 (슬롯 1개일 때만 동작)
            (
                f"--bind=ctrl-s:execute("
                f"python3 {script_path} --tmux-split-add {{-1}}"
                f" --sessions-cache {cache_file})"
                f"+reload({_reload_with_cache})"
            ),
            # ctrl-n: 새 Claude 세션 생성 (디렉터리 선택)
            (
                f"--bind=ctrl-n:execute("
                f"python3 {script_path} --tmux-new-session"
                f" --sessions-cache {cache_file})"
                f"+reload({_reload_fresh})"
            ),
            # ctrl-c: 현재 동작 취소 (fzf 종료 방지)
            f"--bind=ctrl-c:ignore",
            # ctrl-z: tmux detach (세션/프로세스 유지, cs로 재진입)
            f"--bind=ctrl-z:execute-silent(tmux detach-client)",
            # ctrl-q: 세션 완전 종료
            f"--bind=ctrl-q:execute-silent(tmux kill-session -t {tmux_session})+abort",
            "--bind=ctrl-p:toggle-preview",
            "--bind=shift-down:preview-down",
            "--bind=shift-up:preview-up",
            # ctrl-d: 삭제 후 파일에서 새로 로드 (삭제된 항목 제거)
            (
                f"--bind=ctrl-d:execute(python3 {script_path}"
                f" --fzf-action delete {{-1}} --sessions-cache {cache_file})"
                f"+reload({_reload_fresh})"
            ),
            # ctrl-t: 제목 편집 후 새로 로드 (title override 반영)
            (
                f"--bind=ctrl-t:execute(python3 {script_path}"
                f" --fzf-action edit-title {{-1}} --sessions-cache {cache_file})"
                f"+reload({_reload_fresh})"
            ),
            # 정렬 변경: 디스크에서 새로 로드 (ctrl-r로 새 세션도 반영 가능)
            f"--bind=ctrl-r:reload({_reload_fresh} --sort date)",
            f"--bind=ctrl-o:reload({_reload_fresh} --sort project)",
        ],
        input="\n".join(lines),
        text=True,
    )


def run_tmux_layout() -> None:
    """tmux 레이아웃 실행.

    레이아웃:
      [실행 전]
      ┌────────────────────────────────────┐
      │  fzf 세션 브라우저 (전체 화면)      │
      └────────────────────────────────────┘

      [Enter 후]
      ┌──────────────────┬─────────────────┐
      │  fzf 브라우저    │  claude 세션    │
      │  (계속 실행)     │  (새로 열림)    │
      └──────────────────┴─────────────────┘

    cs 재실행 시 기존 tmux 세션 재attach.
    """
    if not shutil.which("tmux"):
        sys.exit("tmux가 필요합니다. sudo apt install tmux")

    tmux_session = "claude-browser"
    script_path = Path(__file__).resolve()

    # 이미 실행 중이면 재attach — fzf pane(index 0)이 살아있을 때만
    if subprocess.run(
        ["tmux", "has-session", "-t", tmux_session], capture_output=True
    ).returncode == 0:
        fzf_alive = subprocess.run(
            ["tmux", "list-panes", "-t", f"{tmux_session}:0", "-F", "#{pane_index}"],
            capture_output=True, text=True,
        ).stdout.strip().splitlines()
        if "0" in fzf_alive:
            subprocess.run(["tmux", "attach-session", "-t", tmux_session])
            return
        # fzf pane이 죽은 상태 → 세션 제거 후 재시작
        subprocess.run(["tmux", "kill-session", "-t", tmux_session], capture_output=True)

    cache_file = "/tmp/claude-browser-cache.json"
    query_file = "/tmp/claude-browser-query.txt"
    Path(query_file).write_text("", encoding="utf-8")
    # 새 세션 시작 시 상태 초기화 (이전 실행의 stale 데이터 제거)
    _write_state({"slots": [], "background": []})

    # tmux 세션 생성 (detached)
    subprocess.run(["tmux", "new-session", "-d", "-s", tmux_session])
    # 마우스 활성화: 스크롤 시 copy mode 진입 (claude 대화 내용 스크롤 가능)
    subprocess.run(["tmux", "set-option", "-t", tmux_session, "mouse", "on"])

    # fzf 브라우저 실행 — 오류 시 메시지 표시 후 Enter 대기, 정상 종료 시 detach
    browser_cmd = (
        f"stty -ixon; python3 {script_path} --tmux-browser"
        f" --sessions-cache {cache_file}"
        f" --query-file {query_file}"
        f" || (echo ''; echo '[cs 오류] 위 메시지를 확인하세요. Enter로 종료...'; read _)"
        f"; tmux detach-client 2>/dev/null"
    )
    subprocess.run(["tmux", "send-keys", "-t", f"{tmux_session}:0", browser_cmd, "Enter"])

    # attach (블로킹 — detach 또는 세션 종료까지)
    subprocess.run(["tmux", "attach-session", "-t", tmux_session])


# ─── 기존 fzf 단독 모드 ───────────────────────────────────────────────────────

def run_fzf(sessions: list[dict]) -> dict | None:
    """fzf로 세션 선택 후 반환. --no-tmux 모드에서 사용."""
    import tempfile

    sessions = sorted(sessions, key=lambda s: s.get("modified", ""), reverse=True)
    lines = [format_session_line(s) for s in sessions]
    id_map = {s["sessionId"]: s for s in sessions}
    script_path = Path(__file__).resolve()

    cache_file = None
    action_file = None
    query_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tf:
            json.dump(sessions, tf, ensure_ascii=False)
            cache_file = tf.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as af:
            action_file = af.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as qf:
            qf.write("")
            query_file = qf.name

        subprocess.run(
            [
                "fzf",
                "--ansi", "--exact", "--height=90%",
                "--layout=reverse", "--border",
                "--prompt=세션 검색> ",
                "--header=Enter:Resume  Ctrl-D:삭제  Ctrl-T:제목편집  Ctrl-P:미리보기토글  Ctrl-C:닫기\nShift+↓↑:미리보기스크롤  Ctrl-R:날짜정렬  Ctrl-O:프로젝트정렬",
                "--color=hl:#ffaf00,hl+:#ffaf00",
                f"--preview=python3 {script_path} --preview-id {{-1}} --sessions-cache {cache_file} --query-file {query_file}",
                "--preview-window=bottom:40%:wrap",
                f"--bind=change:execute-silent(printf '%s' {{q}} > {query_file})+refresh-preview",
                f"--bind=enter:execute(printf 'resume:%s' {{-1}} > {action_file} 2>/dev/null)+abort",
                (
                    f"--bind=ctrl-d:execute(python3 {script_path}"
                    f" --fzf-action delete {{-1}} --sessions-cache {cache_file})"
                    f"+reload(python3 {script_path} --fzf-list-lines)"
                ),
                (
                    f"--bind=ctrl-t:execute(python3 {script_path}"
                    f" --fzf-action edit-title {{-1}} --sessions-cache {cache_file})"
                    f"+reload(python3 {script_path} --fzf-list-lines)"
                ),
                "--bind=ctrl-p:toggle-preview",
                "--bind=shift-down:preview-down",
                "--bind=shift-up:preview-up",
                f"--bind=ctrl-r:reload(python3 {script_path} --fzf-list-lines --sort date)",
                f"--bind=ctrl-o:reload(python3 {script_path} --fzf-list-lines --sort project)",
            ],
            input="\n".join(lines),
            text=True,
        )

        action_path = Path(action_file)
        if action_path.exists():
            content = action_path.read_text().strip()
            if content.startswith("resume:"):
                session_id = content[len("resume:"):]
                return id_map.get(session_id)

        return None
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return None
    finally:
        if cache_file:
            Path(cache_file).unlink(missing_ok=True)
        if action_file:
            Path(action_file).unlink(missing_ok=True)
        if query_file:
            Path(query_file).unlink(missing_ok=True)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="cs",
        description="Claude Code 세션 브라우저",
    )
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--list", action="store_true", help="rich 트리로 출력")
    parser.add_argument("--stats", action="store_true", help="통계 요약 출력")
    parser.add_argument("--clean", action="store_true", help="30일 이상 지난 세션 정리")
    parser.add_argument("--claude-mode", action="store_true", help="Claude용 평문 텍스트 출력")
    parser.add_argument("--filter", metavar="KEYWORD", default="")
    parser.add_argument("--no-tmux", action="store_true", help="tmux 없이 fzf 단독 실행")
    parser.add_argument("--preview-id", metavar="SESSION_ID", help=argparse.SUPPRESS)
    parser.add_argument("--sessions-cache", metavar="PATH", help=argparse.SUPPRESS)
    parser.add_argument("--fzf-list-lines", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--sort", choices=["date", "project"], default="date", help=argparse.SUPPRESS)
    parser.add_argument("--fzf-action", nargs="+", metavar=("ACTION", "SESSION_ID"), help=argparse.SUPPRESS)
    parser.add_argument("--highlight", nargs="*", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--query-file", metavar="PATH", help=argparse.SUPPRESS)
    # tmux 내부 실행용
    parser.add_argument("--tmux-browser", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--tmux-split-open", metavar="SESSION_ID", help=argparse.SUPPRESS)
    parser.add_argument("--tmux-split-add", metavar="SESSION_ID", help=argparse.SUPPRESS)
    parser.add_argument("--tmux-new-session", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "action", nargs="?", default=None,
        help="install: ~/.local/bin/cs 심링크 설치"
    )

    args = parser.parse_args()

    # fzf preview 모드
    if args.preview_id:
        if args.sessions_cache:
            try:
                sessions = json.loads(Path(args.sessions_cache).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                sessions = load_all_sessions()
        else:
            sessions = load_all_sessions()

        session = next((s for s in sessions if s.get("sessionId") == args.preview_id), None)
        if session:
            highlight = ""
            if args.query_file:
                try:
                    highlight = Path(args.query_file).read_text(encoding="utf-8").strip()
                except OSError:
                    pass
            if not highlight and args.highlight:
                highlight = " ".join(args.highlight)
            output = format_session_preview(session, highlight=highlight)
        else:
            output = f"세션을 찾을 수 없습니다: {args.preview_id}"
        print(output)
        return

    # tmux 내부: 오른쪽 분할 열기
    if args.tmux_split_open:
        tmux_split_open(args.tmux_split_open, args.sessions_cache or "")
        return

    if args.tmux_split_add:
        tmux_split_add(args.tmux_split_add, args.sessions_cache or "")
        return

    if args.tmux_new_session:
        tmux_new_session(args.sessions_cache or "")
        return

    # tmux 내부: fzf 브라우저 실행
    if args.tmux_browser:
        run_fzf_tmux(
            cache_file=args.sessions_cache or "",
            query_file=args.query_file or "",
        )
        return

    # fzf reload용
    if args.fzf_list_lines:
        # 캐시가 있으면 사용 (_searchContent 미리 계산됨), 없으면 파일에서 새로 로드
        sessions = None
        if args.sessions_cache:
            try:
                sessions = json.loads(Path(args.sessions_cache).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        if sessions is None:
            sessions = load_all_sessions()

        if args.sort == "project":
            sessions.sort(key=lambda s: (s.get("projectPath", ""), s.get("modified", "")))
        else:
            sessions.sort(key=lambda s: s.get("modified", ""), reverse=True)

        # 서버사이드 쿼리 필터 적용
        query = ""
        if args.query_file:
            try:
                query = Path(args.query_file).read_text(encoding="utf-8").strip()
            except OSError:
                pass
        if query:
            sessions = filter_sessions_by_query(sessions, query)

        slot_ids, bg_ids = get_tmux_open_sessions()
        for s in sessions:
            print(format_session_line(s, slot_ids=slot_ids, bg_ids=bg_ids))
        return

    # fzf 액션: delete / edit-title
    if args.fzf_action:
        fzf_action_name = args.fzf_action[0]
        fzf_session_id = args.fzf_action[1] if len(args.fzf_action) > 1 else ""

        if args.sessions_cache:
            try:
                cached = json.loads(Path(args.sessions_cache).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                cached = load_all_sessions()
        else:
            cached = load_all_sessions()

        target = next((s for s in cached if s.get("sessionId") == fzf_session_id), None)
        if not target:
            print(f"\n  세션을 찾을 수 없습니다: {fzf_session_id}")
            return

        summary = get_display_summary(target)

        if fzf_action_name == "delete":
            confirm = _tty_input(f"\n  삭제: '{summary[:40]}' (y/N) ").strip().lower()
            if confirm == "y":
                delete_session(target)
                sys.stderr.write("  삭제 완료.\n")
                sys.stderr.flush()

        elif fzf_action_name == "edit-title":
            new_title = _tty_input(f"\n  새 제목 (현재: {summary[:40]}): ").strip()
            if new_title:
                save_title_override(fzf_session_id, new_title)
                sys.stderr.write(f"  저장됨: {new_title}\n")
                sys.stderr.flush()
        return

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

    # 기본: tmux가 있으면 분할 레이아웃, 없거나 --no-tmux면 fzf 단독
    if not shutil.which("fzf"):
        print("fzf가 설치되지 않았습니다.")
        print("fzf 설치: sudo apt install fzf  또는  brew install fzf")
        print()
        print_tree(sessions)
        return

    if shutil.which("tmux") and not args.no_tmux:
        run_tmux_layout()
        return

    # --no-tmux 또는 tmux 없을 때: fzf 단독 모드
    selected = run_fzf(sessions)
    if selected:
        project_path = selected.get("projectPath", "")
        session_id = selected.get("sessionId", "")
        summary = get_display_summary(selected)
        print(f"\n{'─' * 60}")
        print(f"  Resume: {summary[:55]}")
        print(f"  프로젝트: {project_path}")
        print(f"{'─' * 60}\n")
        cmd = f'cd "{project_path}" && claude --resume {session_id}'
        os.execlp("bash", "bash", "-c", cmd)


if __name__ == "__main__":
    main()
