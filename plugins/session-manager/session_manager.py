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
