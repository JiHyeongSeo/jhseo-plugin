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
