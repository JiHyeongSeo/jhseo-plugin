#!/usr/bin/env python3
"""cs: AI session browser — Claude/Gemini sessions, tmux multi-slot, fzf search"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

VERSION = "2.5.0"
SUMMARY_CACHE_DIR = Path.home() / ".claude" / "session-summaries"

PROJECTS_DIR = Path.home() / ".claude" / "projects"
TITLE_OVERRIDES_FILE = Path.home() / ".claude" / "session-manager-titles.json"
GEMINI_DIR = Path.home() / ".gemini"


def extract_messages_for_summary(full_path: str, max_messages: int = 150) -> str:
    """JSONL에서 user/assistant 메시지를 추출해 요약용 텍스트 반환."""
    lines_out: list[str] = []
    count = 0
    try:
        raw = Path(full_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
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
        text = text.strip()
        if not text or "Caveat:" in text[:50]:
            continue
        prefix = "사용자" if rtype == "user" else "Claude"
        lines_out.append(f"{prefix}: {text[:500]}")
        count += 1
        if count >= max_messages:
            break
    return "\n\n".join(lines_out)


def get_or_generate_summary(session: dict) -> str:
    """세션 요약 반환. 캐시 유효하면 캐시, 아니면 claude -p로 생성 후 캐시 저장."""
    session_id = session.get("sessionId", "")
    full_path = session.get("fullPath", "")
    current_mtime: int = session.get("fileMtime", 0)

    if not session_id:
        return "(세션 ID 없음)"

    SUMMARY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = SUMMARY_CACHE_DIR / f"{session_id}.json"

    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached.get("mtime") == current_mtime and cached.get("summary"):
                return cached["summary"]
        except (json.JSONDecodeError, OSError):
            pass

    messages_text = extract_messages_for_summary(full_path)
    if not messages_text:
        return "(대화 내용 없음)"

    prompt = (
        "다음 Claude 대화 세션을 compact 요약해줘.\n"
        "포함할 것: 작업 목표, 주요 결정사항, 완료된 작업, 현재 상태, "
        "중요한 코드/설정/파일 경로.\n"
        "다음 세션에서 이 요약만 보고 바로 작업을 이어갈 수 있을 정도로 상세하게.\n\n"
        f"{messages_text}"
    )

    sys.stderr.write("  요약 생성 중 (claude -p)...\n")
    sys.stderr.flush()

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=180,
        )
        summary = result.stdout.strip()
        if not summary:
            return f"(요약 생성 실패: {result.stderr[:200]})"
    except subprocess.TimeoutExpired:
        return "(요약 생성 타임아웃 — 180초 초과)"
    except FileNotFoundError:
        return "(claude CLI를 찾을 수 없습니다)"
    except OSError:
        return "(요약 생성 실패: 시스템 오류)"

    try:
        cache_path.write_text(
            json.dumps({"mtime": current_mtime, "summary": summary}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        pass

    return summary


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


def _parse_gemini_chat_file(chat_file: Path) -> tuple[str, list[dict], str, str]:
    """Gemini 세션 파일(.json/.jsonl) 파싱 → (sessionId, messages, startTime, lastUpdated)."""
    raw = chat_file.read_text(encoding="utf-8", errors="replace")
    session_id = chat_file.stem
    messages: list[dict] = []
    start_time = ""
    last_updated = ""

    if chat_file.suffix == ".jsonl":
        # 새 형식: 첫 줄=메타데이터, 이후 줄=메시지 또는 $set
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "sessionId" in obj:
                session_id = obj.get("sessionId", session_id)
                start_time = obj.get("startTime", "")
                last_updated = obj.get("lastUpdated", "")
            elif "$set" in obj:
                last_updated = obj["$set"].get("lastUpdated", last_updated)
            elif "type" in obj:
                messages.append(obj)
    else:
        # 구 형식: 단일 JSON 객체
        data = json.loads(raw)
        session_id = data.get("sessionId", session_id)
        messages = data.get("messages", [])
        start_time = data.get("startTime", "")
        last_updated = data.get("lastUpdated", "")

    return session_id, messages, start_time, last_updated


def load_gemini_sessions() -> list[dict]:
    """~/.gemini/tmp/*/chats/session-*.{json,jsonl} 에서 Gemini 세션 로드."""
    if not shutil.which("gemini"):
        return []
    tmp_dir = GEMINI_DIR / "tmp"
    if not tmp_dir.exists():
        return []

    projects_file = GEMINI_DIR / "projects.json"
    name_to_path: dict[str, str] = {}
    try:
        data = json.loads(projects_file.read_text(encoding="utf-8"))
        for path, name in data.get("projects", {}).items():
            name_to_path[name] = path
    except (OSError, json.JSONDecodeError):
        pass

    overrides = load_title_overrides()
    sessions = []
    for proj_dir in tmp_dir.iterdir():
        if not proj_dir.is_dir():
            continue
        chats_dir = proj_dir / "chats"
        if not chats_dir.exists():
            continue
        project_path = name_to_path.get(proj_dir.name, "")
        if not project_path:
            history_root = GEMINI_DIR / "history" / proj_dir.name / ".project_root"
            try:
                project_path = history_root.read_text(encoding="utf-8").strip()
            except OSError:
                pass

        # .json(구) 와 .jsonl(신) 모두 처리
        chat_files = list(chats_dir.glob("session-*.json")) + list(chats_dir.glob("session-*.jsonl"))
        seen: set[str] = set()
        for chat_file in chat_files:
            try:
                session_id, messages, start_time, last_updated = _parse_gemini_chat_file(chat_file)
                if session_id in seen:
                    continue
                seen.add(session_id)
                first_prompt = ""
                for msg in messages:
                    if msg.get("type") == "user":
                        content = msg.get("content", [])
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and "text" in c:
                                    first_prompt = c["text"][:200]
                                    break
                        elif isinstance(content, str):
                            first_prompt = content[:200]
                        break
                summary = overrides.get(session_id) or first_prompt[:60] or "Gemini session"
                sessions.append({
                    "sessionId": session_id,
                    "tool": "gemini",
                    "projectPath": project_path,
                    "fullPath": str(chat_file),
                    "summary": summary,
                    "firstPrompt": first_prompt,
                    "messageCount": len(messages),
                    "created": start_time,
                    "modified": last_updated,
                    "gitBranch": "",
                })
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                pass
    return sessions


def load_all_sessions() -> list[dict]:
    """~/.claude/projects/ 아래 모든 세션을 반환."""
    sessions = []
    indexed_ids: set[str] = set()

    for index_file in PROJECTS_DIR.glob("*/sessions-index.json"):
        try:
            data = json.loads(index_file.read_text(encoding="utf-8"))
            entries = data.get("entries", [])
            for entry in entries:
                # .jsonl 실제 존재 여부 검증: 인덱스가 stale 상태로 복원되어
                # 삭제된 세션이 부활하는 현상 방지
                full_path = entry.get("fullPath", "")
                if full_path and not Path(full_path).exists():
                    continue
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

    sessions += load_gemini_sessions()
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
    """입력 프롬프트. tmux popup 우선, 실패 시 /dev/tty fallback."""
    import tempfile as _tempfile
    tmp = Path(_tempfile.mkstemp(suffix=".cs-input.txt")[1])
    try:
        # tmux popup: 플로팅 창에서 입력
        escaped = prompt.replace("'", "'\\''")
        subprocess.run(
            ["tmux", "display-popup", "-E",
             f"printf '{escaped}' && read -r _cs_title && printf '%s' \"$_cs_title\" > {tmp}"],
            capture_output=True,
        )
        if tmp.exists():
            raw = tmp.read_bytes()
            try:
                value = raw.decode("utf-8").strip()
            except UnicodeDecodeError:
                value = raw.decode("cp949", errors="replace").strip()
            return value
        return ""
    except (OSError, FileNotFoundError):
        pass
    finally:
        tmp.unlink(missing_ok=True)

    # fallback: /dev/tty
    try:
        with open("/dev/tty", "r") as tty:
            sys.stderr.write(prompt)
            sys.stderr.flush()
            return tty.readline().rstrip("\n")
    except (OSError, EOFError):
        return ""
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
        return {}


def _write_state(state: dict) -> None:
    _STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


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


def _get_active_pane_id(tmux_session: str) -> str:
    """window 0의 현재 활성 pane ID 반환. split/join 직후 호출하면 새 pane ID를 반환."""
    r = subprocess.run(
        ["tmux", "display-message", "-t", f"{tmux_session}:0", "-p", "#{pane_id}"],
        capture_output=True, text=True,
    )
    return r.stdout.strip()


def fzf_inject_context(source_session_id: str, sessions_cache_path: str) -> None:
    """Ctrl+M: 소스 세션 compact 요약을 대상 Claude pane에 주입."""
    # 소스: 캐시에서 빠르게 조회 (메인 fzf에서 하이라이트된 세션이므로 캐시에 존재)
    cached: list[dict] = []
    if sessions_cache_path:
        try:
            cached = json.loads(Path(sessions_cache_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass

    source = next((s for s in cached if s.get("sessionId") == source_session_id), None)

    # 대상 선택: 항상 최신 스캔 (캐시 이후 생긴 세션도 표시)
    fresh = load_all_sessions()
    if not source:
        source = next((s for s in fresh if s.get("sessionId") == source_session_id), None)
    if not source:
        sys.stderr.write("\n  소스 세션을 찾을 수 없습니다.\n")
        sys.stderr.flush()
        return

    slot_ids, bg_ids = get_tmux_open_sessions()
    open_ids = slot_ids | bg_ids
    _lines = []
    for s in fresh:
        sid = s.get("sessionId", "")
        indicator = "\x1b[32m[열림]\x1b[0m" if sid in open_ids else "\x1b[90m[닫힘]\x1b[0m"
        date = s.get("modified", "")[:10]
        project = s.get("projectPath", "?").split("/")[-1]
        summary = get_display_summary(s)[:50]
        _lines.append(f"{indicator} {date}  {project:<20}  {summary}  {sid}")
    _pick = subprocess.run(
        ["fzf", "--ansi", "--layout=reverse",
         "--prompt=주입할 세션 선택> ", "--header=Enter:선택  Esc:취소",
         "--with-nth=1..-2"],
        input="\n".join(_lines), stdout=subprocess.PIPE, text=True,
    )
    target_id = _pick.stdout.strip().split()[-1] if _pick.returncode == 0 and _pick.stdout.strip() else None
    if not target_id:
        return

    if target_id == source_session_id:
        sys.stderr.write("\n  소스와 대상이 동일합니다.\n")
        sys.stderr.flush()
        return

    # 대상이 닫혀 있으면 먼저 오픈
    if target_id not in (slot_ids | bg_ids):
        sys.stderr.write("\n  대상 세션 오픈 중...\n")
        sys.stderr.flush()
        tmux_split_open(target_id, sessions_cache_path)
        time.sleep(0.3)  # tmux_split_open의 state 쓰기 완료 대기

    # 오픈 후 state 재조회
    state = _read_state()
    slots = state.get("slots", [])
    target_slot = next((sl for sl in slots if sl.get("session_id") == target_id), None)
    if not target_slot:
        sys.stderr.write("\n  대상 pane을 찾을 수 없습니다.\n")
        sys.stderr.flush()
        return

    target_pane_id = target_slot["pane_id"]

    summary = get_or_generate_summary(source)
    title = get_display_summary(source)
    date = source.get("modified", "")[:10]
    formatted = f"[세션 참조: {title} / {date}]\n{summary}\n---"

    # 대상 패널이 Gemini(node)인지 확인
    pane_cmd_result = subprocess.run(
        ["tmux", "display-message", "-p", "-t", target_pane_id, "#{pane_current_command}"],
        capture_output=True, text=True,
    )
    target_is_gemini = pane_cmd_result.stdout.strip() == "node"

    # Gemini 대상: shell mode 방지를 위해 Escape 먼저 전송
    if target_is_gemini:
        subprocess.run(
            ["tmux", "send-keys", "-t", target_pane_id, "Escape"],
            capture_output=True,
        )
        time.sleep(0.3)

    # tmux paste-buffer로 주입 (Enter 없음 — 사용자가 확인 후 전송)
    lb_result = subprocess.run(
        ["tmux", "load-buffer", "-"],
        input=formatted,
        text=True,
        capture_output=True,
    )
    if lb_result.returncode != 0:
        sys.stderr.write("\n  버퍼 로드 실패.\n")
        sys.stderr.flush()
        return

    pb_result = subprocess.run(
        ["tmux", "paste-buffer", "-t", target_pane_id],
        capture_output=True,
    )
    if pb_result.returncode != 0:
        sys.stderr.write("\n  주입 실패: pane이 아직 준비되지 않았습니다. 잠시 후 다시 시도하세요.\n")
        sys.stderr.flush()
        return

    sys.stderr.write("\n  컨텍스트 주입 완료.\n")
    sys.stderr.flush()


def get_tmux_open_sessions() -> tuple[set[str], set[str]]:
    """상태 파일에서 우측 pane의 열린 세션 반환."""
    state = _read_state()
    right_session_id = state.get("right_session_id", "")
    slot_ids = {right_session_id} if right_session_id else set()
    return slot_ids, set()


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

    tool = session.get("tool", "claude")
    if tool == "gemini":
        tool_badge = "\x1b[34m[G]\x1b[0m"
    else:
        tool_badge = "\x1b[36m[C]\x1b[0m"
    display = f"{indicator}{tool_badge} {date}  {project:<20}  {summary:<60}  [{branch}] {msgs}msgs"
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


def _resume_cmd(session: dict) -> str:
    """세션의 툴에 맞는 resume 커맨드 반환."""
    session_id = session.get("sessionId", "")
    if session.get("tool") == "gemini":
        return f"gemini --resume {session_id}"
    return f"claude --resume {session_id}"


def delete_session(session: dict) -> None:
    full_path = Path(session.get("fullPath", ""))
    session_id = session.get("sessionId", "")

    try:
        if full_path.exists():
            full_path.unlink()
    except OSError:
        pass

    if session.get("tool") == "gemini":
        return

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
    # Python 버전 체크
    if sys.version_info < (3, 10):
        ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"  ✗ Python {ver} — 3.10 이상 필요")
        sys.exit(1)
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # tmux 버전 체크
    if shutil.which("tmux"):
        tmux_ver = ""
        try:
            out = subprocess.run(["tmux", "-V"], capture_output=True, text=True)
            tmux_ver = out.stdout.strip().split()[-1] if out.stdout else ""
        except OSError:
            pass
        try:
            parts = [int(x) for x in tmux_ver.rstrip("abcdefghijklmnopqrstuvwxyz").split(".")[:2]]
            if parts < [2, 1]:
                print(f"  ✗ tmux {tmux_ver} — 2.1 이상 필요")
                print("    Ubuntu/Debian : sudo apt-get install -y tmux")
                print("    macOS         : brew upgrade tmux")
                sys.exit(1)
        except (ValueError, IndexError):
            pass
        print(f"  ✓ tmux {tmux_ver}")
    else:
        print("  ✗ tmux 없음 (필수)")
        print("    Ubuntu/Debian : sudo apt-get install -y tmux")
        print("    macOS         : brew install tmux")
        sys.exit(1)

    if shutil.which("fzf"):
        fzf_ver = ""
        try:
            out = subprocess.run(["fzf", "--version"], capture_output=True, text=True)
            fzf_ver = out.stdout.strip().split()[0] if out.stdout else ""
        except OSError:
            pass
        try:
            parts = [int(x) for x in fzf_ver.split(".")[:3]]
            if parts < [0, 38, 0]:
                print(f"  ✗ fzf {fzf_ver} — 0.38.0 이상 필요")
                print("    Ubuntu/Debian : sudo apt-get install -y fzf  (버전이 낮으면 snap/binary로 설치)")
                print("    macOS         : brew upgrade fzf")
                sys.exit(1)
        except (ValueError, IndexError):
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

    if shutil.which("lazygit"):
        print("  ✓ lazygit")
    else:
        print("  - lazygit 미설치 (선택: Ctrl+G git 현황)")
        print("    설치: cs --install-lazygit")

    if shutil.which("yazi"):
        print("  ✓ yazi")
    else:
        print("  - yazi 미설치 (선택: Ctrl+E IDE 레이아웃)")
        print("    설치: cs --install-yazi")


def _install_lazygit() -> bool:
    """lazygit 최신 버전을 ~/.local/bin/ 에 다운로드 설치 (sudo 불필요)."""
    import urllib.request
    import tarfile as _tarfile

    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    dest = bin_dir / "lazygit"

    try:
        print("  lazygit 최신 버전 확인 중...")
        with urllib.request.urlopen(
            "https://api.github.com/repos/jesseduffield/lazygit/releases/latest",
            timeout=10,
        ) as r:
            version = json.loads(r.read()).get("tag_name", "").lstrip("v")
    except Exception as e:
        print(f"  버전 확인 실패: {e}")
        return False

    url = (
        f"https://github.com/jesseduffield/lazygit/releases/latest/download/"
        f"lazygit_{version}_Linux_x86_64.tar.gz"
    )
    tmp_tar = Path("/tmp/lazygit.tar.gz")
    tmp_bin = Path("/tmp/lazygit")
    try:
        print(f"  lazygit v{version} 다운로드 중...")
        urllib.request.urlretrieve(url, tmp_tar)
        with _tarfile.open(tmp_tar) as tf:
            tf.extract("lazygit", "/tmp")
        tmp_bin.rename(dest)
        os.chmod(dest, 0o755)
        print(f"  ✓ lazygit v{version} 설치 완료: {dest}")
        return True
    except Exception as e:
        print(f"  설치 실패: {e}")
        return False
    finally:
        tmp_tar.unlink(missing_ok=True)
        tmp_bin.unlink(missing_ok=True)


def _find_git_repos(base_dir: str, max_depth: int = 3) -> list[str]:
    """base_dir 하위의 git 레포지토리 목록 반환."""
    try:
        result = subprocess.run(
            ["find", base_dir, "-maxdepth", str(max_depth),
             "-name", ".git", "-type", "d",
             "!", "-path", "*/.git/*"],
            capture_output=True, text=True, timeout=5,
        )
        return sorted(str(Path(p).parent) for p in result.stdout.strip().splitlines() if p)
    except (subprocess.TimeoutExpired, OSError):
        return []


def _install_yazi() -> bool:
    """yazi 최신 버전을 ~/.local/bin/ 에 설치 (sudo 불필요)."""
    import urllib.request
    import zipfile
    import io as _io

    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    try:
        print("  yazi 최신 버전 확인 중...")
        with urllib.request.urlopen(
            "https://api.github.com/repos/sxyazi/yazi/releases/latest", timeout=10
        ) as r:
            version = json.loads(r.read()).get("tag_name", "")
    except Exception as e:
        print(f"  버전 확인 실패: {e}")
        return False

    url = "https://github.com/sxyazi/yazi/releases/latest/download/yazi-x86_64-unknown-linux-gnu.zip"
    try:
        print(f"  yazi {version} 다운로드 중...")
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        with zipfile.ZipFile(_io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith("/yazi") or name == "yazi":
                    dest = bin_dir / "yazi"
                    dest.write_bytes(zf.read(name))
                    os.chmod(dest, 0o755)
                    print(f"  ✓ yazi {version} 설치 완료: {dest}")
                    return True
        print("  yazi 바이너리를 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"  설치 실패: {e}")
        return False



def navigate_yazi(project_path: str) -> None:
    """yazi pane을 project_path로 이동. yazi 재시작 방식."""
    state = _read_state()
    yazi_pane = state.get("yazi_pane_id", "")
    if not yazi_pane:
        return
    work_dir = project_path if project_path and Path(project_path).is_dir() else str(Path.home())
    yazi_bin = shutil.which("yazi") or "yazi"
    subprocess.run(["tmux", "send-keys", "-t", yazi_pane, "q", ""])
    time.sleep(0.05)
    subprocess.run(["tmux", "send-keys", "-t", yazi_pane, f"{yazi_bin} {work_dir}", "Enter"])


def tmux_open_lazygit(session_id: str, sessions_cache_path: str) -> None:
    """Ctrl+G: 선택된 세션의 프로젝트 디렉터리에서 lazygit을 팝업으로 실행.

    projectPath가 git 레포가 아니면 하위 git 레포 목록을 fzf로 선택.
    """
    # lazygit 설치 확인
    if not shutil.which("lazygit"):
        sys.stderr.write("\n  lazygit 미설치. 설치 중...\n")
        sys.stderr.flush()
        if not _install_lazygit():
            sys.stderr.write("  설치 실패. 수동으로 설치해주세요: https://github.com/jesseduffield/lazygit\n")
            sys.stderr.flush()
            return

    # 세션 projectPath 조회
    sessions: list[dict] = []
    if sessions_cache_path:
        try:
            sessions = json.loads(Path(sessions_cache_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if not sessions:
        sessions = load_all_sessions()

    session = next((s for s in sessions if s.get("sessionId") == session_id), None)
    project_path = session.get("projectPath", "") if session else ""
    work_dir = project_path if project_path and Path(project_path).is_dir() else str(Path.home())

    # projectPath 자체가 git 레포가 아니면 하위 레포 탐색
    if not (Path(work_dir) / ".git").exists():
        sub_repos = _find_git_repos(work_dir)
        if len(sub_repos) == 1:
            work_dir = sub_repos[0]
        elif len(sub_repos) > 1:
            # fzf로 레포 선택
            rel_repos = [r.replace(work_dir + "/", "") for r in sub_repos]
            pick = subprocess.run(
                ["fzf", "--prompt", "git 레포 선택> ",
                 "--height", "50%", "--reverse", "--border",
                 "--header", f"하위 레포 {len(sub_repos)}개 | Enter:선택  Esc:취소"],
                input="\n".join(rel_repos),
                capture_output=True, text=True,
            )
            if pick.returncode != 0 or not pick.stdout.strip():
                return
            work_dir = str(Path(work_dir) / pick.stdout.strip())

    # tmux display-popup으로 플로팅 lazygit 실행
    subprocess.run([
        "tmux", "display-popup",
        "-E", "-w", "95%", "-h", "90%",
        "-d", work_dir,
        "lazygit",
    ])


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

def tmux_split_open(session_id: str, sessions_cache_path: str) -> None:
    """Enter: 선택한 세션을 우측 고정 pane에서 실행 + yazi 프로젝트 경로 이동."""
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
        sessions = load_all_sessions()
        session = next((s for s in sessions if s.get("sessionId") == session_id), None)
    if not session:
        return

    project_path = session.get("projectPath", "")
    work_dir = project_path if project_path and Path(project_path).is_dir() else str(Path.home())

    state = _read_state()
    claude_pane = state.get("claude_pane_id", "")
    if not claude_pane:
        return

    pane_title = get_display_summary(session)[:60]
    subprocess.run([
        "tmux", "respawn-pane", "-k", "-t", claude_pane, "-c", work_dir,
        _resume_cmd(session),
    ])
    subprocess.run(["tmux", "set-option", "-p", "-t", claude_pane, "@cs_title", pane_title])

    _write_state({**state, "right_session_id": session_id})
    navigate_yazi(work_dir)


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

    # 툴 선택: 설치된 것만 표시
    available_tools = []
    if shutil.which("claude"):
        available_tools.append("Claude  (claude)")
    if shutil.which("gemini"):
        available_tools.append("Gemini  (gemini)")
    if shutil.which("codex"):
        available_tools.append("Codex   (codex)")

    selected_tool = "claude"
    if len(available_tools) > 1:
        tool_result = subprocess.run(
            ["fzf", "--prompt", "도구 선택: ",
             "--height", "40%", "--reverse", "--border",
             "--header", "Enter:선택  Esc:취소"],
            input="\n".join(available_tools),
            capture_output=True, text=True,
        )
        if tool_result.returncode != 0:
            return
        choice = tool_result.stdout.strip().lower()
        if "gemini" in choice:
            selected_tool = "gemini"
        elif "codex" in choice:
            selected_tool = "codex"

    state = _read_state()
    claude_pane = state.get("claude_pane_id", "")
    if not claude_pane:
        return

    subprocess.run([
        "tmux", "respawn-pane", "-k", "-t", claude_pane, "-c", selected_dir,
        selected_tool,
    ])
    subprocess.run([
        "tmux", "set-option", "-p", "-t", claude_pane,
        "@cs_title", f"New: {selected_dir.split('/')[-1]}",
    ])
    _write_state({**state, "right_session_id": ""})
    navigate_yazi(selected_dir)

    # Gemini: 세션 파일 생성까지 대기 (최대 5초 폴링)
    if selected_tool == "gemini":
        chats_before = set(GEMINI_DIR.glob("tmp/*/chats/session-*.json"))
        for _ in range(10):
            time.sleep(0.5)
            chats_after = set(GEMINI_DIR.glob("tmp/*/chats/session-*.json"))
            if chats_after - chats_before:
                break


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

    lines = [" 정렬: 📅 날짜순"] + [format_session_line(s, slot_ids=slot_ids, bg_ids=bg_ids) for s in sessions]
    script_path = Path(__file__).resolve()

    if cache_file:
        try:
            Path(cache_file).write_text(
                json.dumps(sessions, ensure_ascii=False), encoding="utf-8"
            )
        except OSError:
            pass

    header = (
        "Enter:세션열기  Ctrl-N:새세션  Ctrl-P:미리보기토글\n"
        "Tab:다중선택  Ctrl-D:삭제(다중)  Ctrl-T:제목편집  Ctrl-R:정렬토글\n"
        "Ctrl-X:컨텍스트주입  Ctrl-G:Git현황  Ctrl-Z:detach  Ctrl-Q:종료"
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
    # 정렬 토글: sort 상태 파일을 갱신하고 새로 로드
    _toggle_sort = (
        f"printf '%s' {{q}} > {query_file}; "
        f"python3 {script_path} --fzf-toggle-sort --query-file {query_file}"
    )

    # sort 상태 초기화
    try:
        Path("/tmp/claude-browser-sort.txt").write_text("date", encoding="utf-8")
    except OSError:
        pass

    subprocess.run(
        [
            "fzf",
            "--ansi", "--disabled", "--no-sort", "--layout=reverse", "--border",
            "--multi",
            "--header-lines=1",
            "--prompt=세션 검색> ",
            f"--header={header}",
            "--color=hl:#ffaf00,hl+:#ffaf00",
            f"--preview=python3 {script_path} --preview-id {{-1}} --sessions-cache {cache_file} --query-file {query_file}",
            "--preview-window=bottom:40%:wrap:hidden",
            # 검색어 변경 → query 파일 기록 + 서버사이드 필터 reload + preview 갱신
            f"--bind=change:reload({_reload_with_cache})+refresh-preview",
            # 시작 시 green/yellow 점 동기화
            f"--bind=start:reload(python3 {script_path} --fzf-list-lines --sessions-cache {cache_file})",
            # Tab: 다중 선택 후 아래로 이동
            "--bind=tab:toggle+down",
            # Enter: 세션 열고 목록 reload (fresh: 새 세션·삭제 반영)
            (
                f"--bind=enter:execute("
                f"python3 {script_path} --tmux-split-open {{-1}}"
                f" --sessions-cache {cache_file})"
                f"+reload({_reload_fresh})"
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
            # ctrl-d: 선택 항목 삭제 ({+f}로 다중 선택 전달)
            (
                f"--bind=ctrl-d:execute(python3 {script_path}"
                f" --fzf-action delete {{+f}} --sessions-cache {cache_file})"
                f"+reload({_reload_fresh})"
            ),
            # ctrl-t: 제목 편집 후 새로 로드 (title override 반영)
            (
                f"--bind=ctrl-t:execute(python3 {script_path}"
                f" --fzf-action edit-title {{-1}} --sessions-cache {cache_file})"
                f"+reload({_reload_fresh})"
            ),
            # ctrl-r: 정렬 토글 (date ↔ project)
            f"--bind=ctrl-r:reload({_toggle_sort})",
            # ctrl-x: 소스 세션 요약을 대상 pane에 주입
            (
                f"--bind=ctrl-x:execute("
                f"python3 {script_path} --fzf-inject-context {{-1}}"
                f" --sessions-cache {cache_file})"
                f"+reload({_reload_with_cache})"
            ),
            (
                f"--bind=ctrl-g:execute(python3 {script_path} --lazygit {{-1}}"
                f" --sessions-cache {cache_file})"
            ),
        ],
        input="\n".join(lines),
        text=True,
    )


def run_tmux_layout() -> None:
    """cs 기본 모드: 3-pane 워크스페이스 레이아웃.

    레이아웃:
      ┌──────────────────────────────┬──────────────────┐
      │  pane 0: fzf 세션목록        │  pane 2:         │
      │  (상단 30%, 좌 70%)          │  Claude/Gemini   │
      ├──────────────────────────────┤  (우 30%)        │
      │  pane 1: yazi                │                  │
      │  (하단 70%, 좌 70%)          │                  │
      └──────────────────────────────┴──────────────────┘
    """
    if not shutil.which("tmux"):
        sys.exit("tmux가 필요합니다. sudo apt install tmux")

    tmux_session = "claude-browser"
    script_path = Path(__file__).resolve()

    # 이미 실행 중이면 재attach
    if subprocess.run(
        ["tmux", "has-session", "-t", tmux_session], capture_output=True
    ).returncode == 0:
        fzf_alive = subprocess.run(
            ["tmux", "list-panes", "-t", f"{tmux_session}:0", "-F", "#{pane_index}"],
            capture_output=True, text=True,
        ).stdout.strip().splitlines()
        if "0" in fzf_alive:
            if os.environ.get("TMUX"):
                subprocess.run(["tmux", "switch-client", "-t", tmux_session])
            else:
                subprocess.run(["tmux", "attach-session", "-t", tmux_session])
            return
        subprocess.run(["tmux", "kill-session", "-t", tmux_session], capture_output=True)

    cache_file = "/tmp/claude-browser-cache.json"
    query_file = "/tmp/claude-browser-query.txt"
    Path(query_file).write_text("", encoding="utf-8")
    _write_state({})

    # 세션 생성
    subprocess.run(["tmux", "new-session", "-d", "-s", tmux_session])
    subprocess.run(["tmux", "set-option", "-t", tmux_session, "mouse", "on"])
    subprocess.run(["tmux", "set-option", "-t", tmux_session, "pane-border-status", "top"])
    subprocess.run(["tmux", "set-option", "-t", tmux_session, "pane-border-format", " #{@cs_title} "])

    # 우측 30% → claude pane
    subprocess.run(["tmux", "split-window", "-h", "-p", "30", "-t", f"{tmux_session}:0.0"])
    claude_pane = _get_active_pane_id(tmux_session)

    # 좌측 하단 70% → yazi pane
    subprocess.run(["tmux", "split-window", "-v", "-p", "70", "-t", f"{tmux_session}:0.0"])
    yazi_pane = _get_active_pane_id(tmux_session)

    # pane ID 저장
    _write_state({"yazi_pane_id": yazi_pane, "claude_pane_id": claude_pane, "right_session_id": ""})

    # 타이틀 설정
    subprocess.run(["tmux", "set-option", "-p", "-t", f"{tmux_session}:0.0", "@cs_title", "cs"])
    subprocess.run(["tmux", "set-option", "-p", "-t", yazi_pane, "@cs_title", "files"])
    subprocess.run(["tmux", "set-option", "-p", "-t", claude_pane, "@cs_title", "claude"])

    # yazi 시작 (하단 pane)
    yazi_bin = shutil.which("yazi") or "yazi"
    subprocess.run(["tmux", "send-keys", "-t", yazi_pane, yazi_bin, "Enter"])

    # fzf 브라우저 시작 (좌상단 pane)
    browser_cmd = (
        f"stty -ixon; python3 {script_path} --tmux-browser"
        f" --sessions-cache {cache_file}"
        f" --query-file {query_file}"
        f" || (echo ''; echo '[cs 오류] Enter로 종료...'; read _)"
        f"; tmux detach-client 2>/dev/null"
    )
    subprocess.run(["tmux", "select-pane", "-t", f"{tmux_session}:0.0"])
    subprocess.run(["tmux", "send-keys", "-t", f"{tmux_session}:0.0", browser_cmd, "Enter"])

    if os.environ.get("TMUX"):
        subprocess.run(["tmux", "switch-client", "-t", tmux_session])
    else:
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

        _toggle_sort = (
            f"printf '%s' {{q}} > {query_file}; "
            f"python3 {script_path} --fzf-toggle-sort --sessions-cache {cache_file} --query-file {query_file}"
        )
        _reload_fresh = (
            f"printf '%s' {{q}} > {query_file}; "
            f"python3 {script_path} --fzf-list-lines --query-file {query_file}"
        )
        Path("/tmp/claude-browser-sort.txt").write_text("date", encoding="utf-8")

        subprocess.run(
            [
                "fzf",
                "--ansi", "--exact", "--height=90%",
                "--layout=reverse", "--border",
                "--prompt=세션 검색> ",
                "--header=Enter:Resume  Ctrl-D:삭제(다중)  Ctrl-T:제목편집  Ctrl-P:미리보기토글  Ctrl-C:닫기\nShift+↓↑:미리보기스크롤  Tab:다중선택  Ctrl-R:정렬토글",
                "--multi",
                "--color=hl:#ffaf00,hl+:#ffaf00",
                f"--preview=python3 {script_path} --preview-id {{-1}} --sessions-cache {cache_file} --query-file {query_file}",
                "--preview-window=bottom:40%:wrap:hidden",
                f"--bind=change:execute-silent(printf '%s' {{q}} > {query_file})+refresh-preview",
                f"--bind=enter:execute(printf 'resume:%s' {{-1}} > {action_file} 2>/dev/null)+abort",
                "--bind=tab:toggle+down",
                (
                    f"--bind=ctrl-d:execute(python3 {script_path}"
                    f" --fzf-action delete {{+f}} --sessions-cache {cache_file})"
                    f"+reload({_reload_fresh})"
                ),
                (
                    f"--bind=ctrl-t:execute(python3 {script_path}"
                    f" --fzf-action edit-title {{-1}} --sessions-cache {cache_file})"
                    f"+reload({_reload_fresh})"
                ),
                "--bind=ctrl-p:toggle-preview",
                "--bind=shift-down:preview-down",
                "--bind=shift-up:preview-up",
                f"--bind=ctrl-r:reload({_toggle_sort})",
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
    parser.add_argument("--fzf-toggle-sort", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--sort", choices=["date", "project"], default="date", help=argparse.SUPPRESS)
    parser.add_argument("--fzf-action", nargs="+", metavar=("ACTION", "SESSION_ID"), help=argparse.SUPPRESS)
    parser.add_argument("--fzf-inject-context", metavar="SESSION_ID", help=argparse.SUPPRESS)
    parser.add_argument("--lazygit", metavar="SESSION_ID", help=argparse.SUPPRESS)
    parser.add_argument("--install-lazygit", action="store_true", help="lazygit 설치")
    parser.add_argument("--install-yazi", action="store_true", help="yazi 설치")
    parser.add_argument("--highlight", nargs="*", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--query-file", metavar="PATH", help=argparse.SUPPRESS)
    # tmux 내부 실행용
    parser.add_argument("--tmux-browser", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--tmux-split-open", metavar="SESSION_ID", help=argparse.SUPPRESS)
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

        # sort 상태 파일 우선 (검색어 변경 reload 시에도 정렬 유지)
        sort_mode = "date"
        try:
            sort_mode = Path("/tmp/claude-browser-sort.txt").read_text(encoding="utf-8").strip()
        except OSError:
            pass

        if sort_mode == "project":
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
        sort_label = "📁 프로젝트순" if sort_mode == "project" else "📅 날짜순"
        print(f" 정렬: {sort_label}")
        for s in sessions:
            print(format_session_line(s, slot_ids=slot_ids, bg_ids=bg_ids))
        return

    # 정렬 토글: date ↔ project 순환 후 목록 출력
    if args.fzf_toggle_sort:
        _sort_file = Path("/tmp/claude-browser-sort.txt")
        try:
            current_sort = _sort_file.read_text(encoding="utf-8").strip()
        except OSError:
            current_sort = "date"
        new_sort = "project" if current_sort == "date" else "date"
        try:
            _sort_file.write_text(new_sort, encoding="utf-8")
        except OSError:
            pass

        sessions = None
        if args.sessions_cache:
            try:
                sessions = json.loads(Path(args.sessions_cache).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        if sessions is None:
            sessions = load_all_sessions()

        if new_sort == "project":
            sessions.sort(key=lambda s: (s.get("projectPath", ""), s.get("modified", "")))
        else:
            sessions.sort(key=lambda s: s.get("modified", ""), reverse=True)

        query = ""
        if args.query_file:
            try:
                query = Path(args.query_file).read_text(encoding="utf-8").strip()
            except OSError:
                pass
        if query:
            sessions = filter_sessions_by_query(sessions, query)

        slot_ids, bg_ids = get_tmux_open_sessions()
        sort_label = "📁 프로젝트순" if new_sort == "project" else "📅 날짜순"
        print(f" 정렬: {sort_label}")
        for s in sessions:
            print(format_session_line(s, slot_ids=slot_ids, bg_ids=bg_ids))
        return

    if args.fzf_inject_context:
        fzf_inject_context(args.fzf_inject_context, args.sessions_cache or "")
        return

    if args.lazygit:
        tmux_open_lazygit(args.lazygit, args.sessions_cache or "")
        return

    if args.install_lazygit:
        _install_lazygit()
        return

    if args.install_yazi:
        _install_yazi()
        return

    # fzf 액션: delete / edit-title
    if args.fzf_action:
        fzf_action_name = args.fzf_action[0]
        fzf_arg = args.fzf_action[1] if len(args.fzf_action) > 1 else ""

        if args.sessions_cache:
            try:
                cached = json.loads(Path(args.sessions_cache).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                cached = load_all_sessions()
        else:
            cached = load_all_sessions()

        if fzf_action_name == "delete":
            # {+f}: fzf가 선택 항목을 파일로 전달 (다중 선택 지원)
            arg_path = Path(fzf_arg)
            if arg_path.exists():
                session_ids = [
                    line.strip().split()[-1]
                    for line in arg_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
            else:
                session_ids = [fzf_arg] if fzf_arg else []

            targets = [s for s in cached if s.get("sessionId") in session_ids]
            # cache stale → 디스크에서 재로드 후 재시도
            if len(targets) < len(session_ids):
                fresh = load_all_sessions()
                cached_ids = {s.get("sessionId") for s in targets}
                missing = [sid for sid in session_ids if sid not in cached_ids]
                targets += [s for s in fresh if s.get("sessionId") in missing]
            if not targets:
                sys.stderr.write("\n  세션을 찾을 수 없습니다.\n")
                sys.stderr.flush()
                return

            if len(targets) == 1:
                label = f"'{get_display_summary(targets[0])[:40]}'"
            else:
                label = f"{len(targets)}개 세션"
            confirm = _tty_input(f"\n  삭제: {label} (y/N) ").strip().lower()
            if confirm == "y":
                deleted_ids = {t.get("sessionId") for t in targets}
                for t in targets:
                    delete_session(t)
                # 캐시 파일에서도 삭제 (stale 방지)
                if args.sessions_cache:
                    try:
                        remaining = [s for s in cached if s.get("sessionId") not in deleted_ids]
                        Path(args.sessions_cache).write_text(
                            json.dumps(remaining, ensure_ascii=False), encoding="utf-8"
                        )
                    except OSError:
                        pass
                sys.stderr.write(f"  {len(targets)}개 삭제 완료.\n")
                sys.stderr.flush()
            return

        # edit-title은 단일 세션만
        fzf_session_id = fzf_arg
        target = next((s for s in cached if s.get("sessionId") == fzf_session_id), None)
        if not target:
            print(f"\n  세션을 찾을 수 없습니다: {fzf_session_id}")
            return

        summary = get_display_summary(target)

        if fzf_action_name == "edit-title":
            new_title = _tty_input(f"\n  새 제목 (현재: {summary[:40]}): ").strip()
            if new_title:
                save_title_override(fzf_session_id, new_title)
                # 캐시 파일에서도 제목 갱신 (stale 방지)
                if args.sessions_cache:
                    try:
                        for s in cached:
                            if s.get("sessionId") == fzf_session_id:
                                s["summary"] = new_title
                        Path(args.sessions_cache).write_text(
                            json.dumps(cached, ensure_ascii=False), encoding="utf-8"
                        )
                    except OSError:
                        pass
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
        summary = get_display_summary(selected)
        print(f"\n{'─' * 60}")
        print(f"  Resume: {summary[:55]}")
        print(f"  프로젝트: {project_path}")
        print(f"{'─' * 60}\n")
        cmd = f'cd "{project_path}" && {_resume_cmd(selected)}'
        os.execlp("bash", "bash", "-c", cmd)


if __name__ == "__main__":
    main()
