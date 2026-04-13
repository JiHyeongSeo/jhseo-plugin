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
