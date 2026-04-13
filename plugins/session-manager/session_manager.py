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
            # Claude Code 자동 삽입 시스템 메시지 건너뜀
            # 실제 포맷: <local-command-caveat>Caveat: ...
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
    """~/.claude/projects/ 아래 모든 세션을 반환.

    sessions-index.json이 있는 프로젝트는 인덱스에서,
    없는 프로젝트는 .jsonl 파일을 직접 파싱해서 로드.
    """
    sessions = []
    indexed_dirs: set[Path] = set()

    for index_file in PROJECTS_DIR.glob("*/sessions-index.json"):
        try:
            data = json.loads(index_file.read_text(encoding="utf-8"))
            entries = data.get("entries", [])
            if entries:
                indexed_dirs.add(index_file.parent)
                sessions.extend(entries)
        except (json.JSONDecodeError, OSError):
            pass

    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir() or proj_dir in indexed_dirs:
            continue
        for jsonl_file in proj_dir.glob("*.jsonl"):
            session = parse_jsonl_session(jsonl_file)
            if session:
                sessions.append(session)

    # 사용자 정의 제목 오버라이드 적용
    overrides = load_title_overrides()
    if overrides:
        for s in sessions:
            sid = s.get("sessionId", "")
            if sid in overrides:
                s["summary"] = overrides[sid]

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


def clean_summary(text: str) -> str:
    """XML 태그, 개행 등 불필요한 문자 제거."""
    text = re.sub(r"<[^>]+>", " ", text)  # 완전한 XML 태그 → 공백
    text = re.sub(r"<[^>]*$", "", text)   # 끝에 잘린 불완전 태그 제거
    text = " ".join(text.split())          # 연속 공백·개행 → 단일 공백
    return text.strip()


def _tty_input(prompt: str) -> str:
    """fzf execute() 환경에서도 작동하는 인터랙티브 입력. /dev/tty를 직접 사용."""
    try:
        with open("/dev/tty", "r") as tty:
            sys.stderr.write(prompt)
            sys.stderr.flush()
            return tty.readline().rstrip("\n")
    except OSError:
        return input(prompt)


def load_title_overrides() -> dict[str, str]:
    """사용자 정의 세션 제목 오버라이드 로드."""
    try:
        return json.loads(TITLE_OVERRIDES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_title_override(session_id: str, title: str) -> None:
    """사용자 정의 제목 저장."""
    overrides = load_title_overrides()
    overrides[session_id] = title
    TITLE_OVERRIDES_FILE.write_text(
        json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_display_summary(session: dict) -> str:
    """표시용 요약 반환. XML 정제 + 제목 없으면 [제목 없음] 표시."""
    raw = session.get("summary", "") or session.get("firstPrompt", "")
    cleaned = clean_summary(raw)
    if not cleaned or cleaned == "No summary":
        return "[제목 없음]"
    return cleaned


def format_session_line(session: dict) -> str:
    """세션을 fzf 입력용 한 줄 문자열로 변환. 마지막 토큰은 반드시 sessionId."""
    date = session.get("modified", "")[:10]
    project = session.get("projectPath", "?").split("/")[-1]
    summary = get_display_summary(session)[:60]
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
            summary = get_display_summary(s)[:60]
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
        # rich 없을 때 폴백
        for project_path, entries in groups.items():
            print(f"\n[{project_path}]  ({len(entries)}개)")
            for i, s in enumerate(entries):
                date = s.get("modified", "")[:10]
                summary = get_display_summary(s)[:50]
                branch = s.get("gitBranch", "")
                msgs = s.get("messageCount", 0)
                prefix = "└─" if i == len(entries) - 1 else "├─"
                print(f"  {prefix} {date}  {summary}  [{branch}]  {msgs}msgs")


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


def format_session_preview(session: dict) -> str:
    """세션 대화 내용을 fzf 미리보기용으로 포맷."""
    full_path = Path(session.get("fullPath", ""))
    header = [
        f"프로젝트: {session.get('projectPath', '')}",
        f"날짜:     {session.get('modified', '')[:10]}  |  메시지: {session.get('messageCount', 0)}개",
        f"제목:     {get_display_summary(session)}",
        "─" * 60,
    ]

    if not full_path.exists():
        return "\n".join(header + ["[세션 파일 없음]"])

    messages = []
    msg_count = 0
    try:
        for line in full_path.read_text(encoding="utf-8", errors="replace").splitlines():
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
            if not text:
                continue

            prefix = "👤" if rtype == "user" else "🤖"
            messages.append(f"\n{prefix} {text[:250]}")
            msg_count += 1

    except OSError:
        messages.append("[파일 읽기 오류]")

    return "\n".join(header + messages)


def run_fzf(sessions: list[dict]) -> dict | None:
    """fzf로 세션 선택 후 resume할 세션 반환. 취소하면 None."""
    import tempfile

    lines = [format_session_line(s) for s in sessions]
    id_map = {s["sessionId"]: s for s in sessions}
    script_path = Path(__file__).resolve()

    cache_file = None
    action_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tf:
            json.dump(sessions, tf, ensure_ascii=False)
            cache_file = tf.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as af:
            action_file = af.name

        subprocess.run(
            [
                "fzf",
                "--ansi",
                "--height=90%",
                "--layout=reverse",
                "--border",
                "--prompt=세션 검색> ",
                "--header=Enter:Resume  Ctrl-D:삭제  Ctrl-T:제목편집  →/←:미리보기스크롤  Ctrl-P:토글  Ctrl-C:닫기",
                f"--preview=python3 {script_path} --preview-id {{-1}} --sessions-cache {cache_file}",
                "--preview-window=right:50%:wrap",
                # Enter: 선택한 세션 ID를 파일에 기록 후 fzf 종료 (execute로 블로킹 보장)
                f"--bind=enter:execute(printf 'resume:%s' {{-1}} > {action_file} 2>/dev/null)+abort",
                # Ctrl-D: 삭제 (인터랙티브 확인) + 목록 갱신
                (
                    f"--bind=ctrl-d:execute(python3 {script_path}"
                    f" --fzf-action delete {{-1}} --sessions-cache {cache_file})"
                    f"+reload(python3 {script_path} --fzf-list-lines)"
                ),
                # Ctrl-T: 제목 편집 (인터랙티브) + 목록 갱신
                (
                    f"--bind=ctrl-t:execute(python3 {script_path}"
                    f" --fzf-action edit-title {{-1}} --sessions-cache {cache_file})"
                    f"+reload(python3 {script_path} --fzf-list-lines)"
                ),
                # Ctrl-P: 미리보기 패널 토글
                "--bind=ctrl-p:toggle-preview",
                # →/←: 미리보기 패널 스크롤 (↑↓는 리스트 탐색 유지)
                "--bind=right:preview-down",
                "--bind=left:preview-up",
            ],
            input="\n".join(lines),
            text=True,
        )

        # Enter로 선택 시 action 파일에 기록된 세션 ID 확인
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


def show_action_menu(session: dict) -> None:
    """선택된 세션의 액션 메뉴를 표시하고 실행."""
    summary = get_display_summary(session)
    print()
    print(f"  세션: {summary[:60]}")
    print(f"  프로젝트: {session.get('projectPath', '')}")
    print(f"  날짜: {session.get('modified', '')[:10]}")
    print(f"  ID: {session.get('sessionId', '')}")
    print()
    print("  r) Resume    d) Delete    v) View details    p) Preview    t) Edit title    q) Quit")
    print()

    try:
        choice = input("  선택> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if choice == "r":
        project_path = session.get("projectPath", "")
        session_id = session.get("sessionId", "")
        cmd = f'cd "{project_path}" && claude --resume {session_id}'
        print(f"\n실행: {cmd}\n")
        os.execlp("bash", "bash", "-c", cmd)

    elif choice == "d":
        try:
            confirm = input(
                f"  '{summary[:40]}' 를 삭제하시겠습니까? (y/N) "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if confirm == "y":
            delete_session(session)
            print("  삭제 완료.")

    elif choice == "v":
        print()
        print(f"  Summary     : {summary}")
        print(f"  First prompt: {clean_summary(session.get('firstPrompt', ''))[:120]}")
        print(f"  Created     : {session.get('created', '')}")
        print(f"  Modified    : {session.get('modified', '')}")
        print(f"  Branch      : {session.get('gitBranch', '')}")
        print(f"  Messages    : {session.get('messageCount', 0)}")
        print(f"  Session ID  : {session.get('sessionId', '')}")
        print(f"  Project     : {session.get('projectPath', '')}")

    elif choice == "p":
        preview = format_session_preview(session)
        try:
            pager = subprocess.Popen(["less", "-R"], stdin=subprocess.PIPE)
            pager.communicate(input=preview.encode("utf-8"))
        except (OSError, subprocess.SubprocessError):
            print(preview)

    elif choice == "t":
        try:
            new_title = input(f"  새 제목 (현재: {summary[:40]}): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if new_title:
            save_title_override(session.get("sessionId", ""), new_title)
            session["summary"] = new_title
            print(f"  제목 저장됨: {new_title}")


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
        "--preview-id", metavar="SESSION_ID",
        help="fzf 미리보기용: 해당 세션 내용 출력"
    )
    parser.add_argument("--sessions-cache", metavar="PATH", help=argparse.SUPPRESS)
    parser.add_argument("--fzf-list-lines", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--fzf-action", nargs="+", metavar=("ACTION", "SESSION_ID"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "action", nargs="?", default=None,
        help="install: ~/.local/bin/claude-sessions 심링크 설치"
    )

    args = parser.parse_args()

    # fzf preview 모드: 캐시에서 빠르게 조회 후 출력
    if args.preview_id:
        if args.sessions_cache:
            try:
                sessions = json.loads(
                    Path(args.sessions_cache).read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError):
                sessions = load_all_sessions()
        else:
            sessions = load_all_sessions()
        session = next((s for s in sessions if s.get("sessionId") == args.preview_id), None)
        if session:
            print(format_session_preview(session))
        else:
            print(f"세션을 찾을 수 없습니다: {args.preview_id}")
        return

    # fzf reload용: 최신 세션 목록 한 줄씩 출력
    if args.fzf_list_lines:
        for s in load_all_sessions():
            print(format_session_line(s))
        return

    # fzf execute용: delete / edit-title 액션 처리
    if args.fzf_action:
        fzf_action_name = args.fzf_action[0]
        fzf_session_id = args.fzf_action[1] if len(args.fzf_action) > 1 else ""

        if args.sessions_cache:
            try:
                cached = json.loads(
                    Path(args.sessions_cache).read_text(encoding="utf-8")
                )
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

    # 기본: fzf 인터랙티브 모드
    if not shutil.which("fzf"):
        print("fzf가 설치되지 않았습니다. --list 모드로 전환합니다.")
        print("fzf 설치: sudo apt install fzf  또는  brew install fzf")
        print()
        print_tree(sessions)
        return

    selected = run_fzf(sessions)
    if selected:
        project_path = selected.get("projectPath", "")
        session_id = selected.get("sessionId", "")
        summary = get_display_summary(selected)
        print(f"\n{'─' * 60}")
        print(f"  Resume 세션")
        print(f"  제목    : {summary[:55]}")
        print(f"  프로젝트: {project_path}")
        print(f"  ID      : {session_id}")
        print(f"{'─' * 60}\n")
        cmd = f'cd "{project_path}" && claude --resume {session_id}'
        os.execlp("bash", "bash", "-c", cmd)


if __name__ == "__main__":
    main()
