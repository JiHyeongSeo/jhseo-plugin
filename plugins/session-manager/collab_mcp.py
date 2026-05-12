#!/usr/bin/env python3
"""collab_mcp.py — MCP server for Claude-Gemini collaboration.

Claude Code 협업 패널에서 Gemini(또는 다른 Claude)와 통신하는 MCP 서버.
cs session-manager의 Ctrl+E 레이아웃과 연동합니다.

Tools:
  collab_send(target, message)  → 상대 AI 패널에 메시지 전달
  collab_wait(target, timeout)  → 상대 AI 응답 완료까지 대기 후 반환
  collab_status()               → 현재 협업 세션 상태 확인
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEBATE_STATE_FILE = Path.home() / ".claude" / "cs-debate-state.json"
PROJECTS_DIR = Path.home() / ".claude" / "projects"
GEMINI_DIR = Path.home() / ".gemini"


# ── State ────────────────────────────────────────────────────────────────────

def _read_state() -> dict:
    try:
        return json.loads(DEBATE_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_state(state: dict) -> None:
    try:
        DEBATE_STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


# ── tmux helpers ─────────────────────────────────────────────────────────────

def _send_to_pane(pane_id: str, message: str) -> None:
    # Escape로 shell mode 등 특수 모드 해제 후 전송
    subprocess.run(["tmux", "send-keys", "-t", pane_id, "Escape"], capture_output=True)
    time.sleep(0.3)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(message)
        tmp = f.name
    try:
        subprocess.run(["tmux", "load-buffer", tmp], capture_output=True)
        subprocess.run(["tmux", "paste-buffer", "-t", pane_id], capture_output=True)
        time.sleep(0.2)
        subprocess.run(["tmux", "send-keys", "-t", pane_id, "Enter"])
    finally:
        Path(tmp).unlink(missing_ok=True)


# ── Log file helpers ─────────────────────────────────────────────────────────

def _read_ai_messages(log_file: Path, ai_types: tuple[str, ...]) -> list[str]:
    """Claude/Gemini 로그 파일에서 AI 응답 메시지 목록 반환."""
    results: list[str] = []
    try:
        for line in log_file.read_text(encoding="utf-8").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") not in ai_types:
                continue
            # Claude: obj["message"]["content"], Gemini: obj["content"]
            content = obj.get("message", {}).get("content") or obj.get("content", [])
            if isinstance(content, list):
                parts = [
                    c.get("text", "") for c in content
                    if isinstance(c, dict) and c.get("type") == "text" and c.get("text")
                ]
                text = "\n".join(parts).strip()
            elif isinstance(content, str):
                text = content.strip()
            else:
                continue
            if text:
                results.append(text)
    except OSError:
        pass
    return results


def _wait_for_new_message(
    log_file: Path,
    ai_types: tuple[str, ...],
    known_count: int,
    timeout: int,
) -> str:
    prev_text = ""
    stable_ticks = 0
    for _ in range(timeout * 2):
        time.sleep(0.5)
        messages = _read_ai_messages(log_file, ai_types)
        if len(messages) <= known_count:
            continue
        current = messages[-1]
        if current == prev_text:
            stable_ticks += 1
            if stable_ticks >= 4:
                return current
        else:
            stable_ticks = 0
            prev_text = current
    messages = _read_ai_messages(log_file, ai_types)
    return messages[-1] if len(messages) > known_count else ""


def _find_new_session_file(glob_pattern: str, known: set[str], timeout: int = 30) -> Path | None:
    base = Path.home()
    for _ in range(timeout * 2):
        time.sleep(0.5)
        current = {str(p) for p in base.glob(glob_pattern)}
        new = current - known
        if new:
            return max((Path(p) for p in new), key=lambda p: p.stat().st_mtime)
    return None


# ── Tool config ───────────────────────────────────────────────────────────────

_CLAUDE_TYPES = ("assistant",)
_GEMINI_TYPES = ("gemini", "model", "assistant_model")

def _get_target_config(target: str) -> dict:
    if target == "claude":
        return dict(
            pane_key="claude_pane",
            file_key="claude_session_file",
            count_key="claude_response_count",
            known_key="claude_known_files",
            glob=".claude/projects/*/*.jsonl",
            ai_types=_CLAUDE_TYPES,
        )
    else:
        return dict(
            pane_key="gemini_pane",
            file_key="gemini_session_file",
            count_key="gemini_response_count",
            known_key="gemini_known_files",
            glob=".gemini/tmp/*/chats/session-*.jsonl",
            ai_types=_GEMINI_TYPES,
        )


# ── MCP Tool implementations ──────────────────────────────────────────────────

def tool_collab_ask(tool: str, message: str, keep_pane: bool = False, work_dir: str = "") -> dict:
    """온디맨드 협업: subprocess로 직접 호출해 응답 반환.

    gemini -p "message" 방식 사용 → tmux paste 없음 → ! 문자 문제 없음.
    keep_pane=True면 응답 후 pane을 열어 대화 내용 표시.
    """
    if tool not in ("gemini", "claude"):
        return {"error": f"지원하지 않는 도구: {tool}. 'gemini' 또는 'claude'만 가능합니다."}

    if not work_dir:
        work_dir = str(Path.cwd())

    if tool == "gemini":
        cmd = ["gemini", "-p", message, "-o", "text"]
    else:
        cmd = ["claude", "-p", message]

    # subprocess로 직접 실행 (tmux paste 없이)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=work_dir,
            timeout=120,
        )
    except FileNotFoundError:
        return {"error": f"{tool} CLI를 찾을 수 없습니다. 설치되어 있는지 확인하세요."}
    except subprocess.TimeoutExpired:
        return {"error": f"{tool} 응답 타임아웃 (120초)"}

    response = result.stdout.strip()
    if not response and result.returncode != 0:
        return {"error": f"{tool} 오류: {result.stderr.strip()[:300]}"}

    # keep_pane=True면 결과를 새 tmux pane에 표시
    if keep_pane:
        current_pane = os.environ.get("TMUX_PANE", "")
        if current_pane:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(f"=== {tool} 응답 ===\n\n{response}\n")
                tmp = f.name
            subprocess.run(
                ["tmux", "split-window", "-v", "-l", "40%",
                 "-t", current_pane, f"cat {tmp}; echo; read -p '닫으려면 Enter...'"],
                capture_output=True,
            )

    if response:
        return {"response": response, "tool": tool, "chars": len(response)}
    return {"error": f"{tool}에서 응답이 없습니다."}


def tool_collab_send(target: str, message: str) -> dict:
    state = _read_state()
    cfg = _get_target_config(target)
    pane_id = state.get(cfg["pane_key"], "")
    if not pane_id:
        return {"error": f"{target} 패널 없음. Ctrl+E로 협업 레이아웃을 먼저 시작하세요."}
    _send_to_pane(pane_id, message)
    return {"ok": True, "target": target, "chars": len(message)}


def tool_collab_wait(target: str, timeout: int = 120) -> dict:
    state = _read_state()
    cfg = _get_target_config(target)

    # 세션 파일 확보
    session_path = state.get(cfg["file_key"], "")
    if session_path:
        session_file = Path(session_path)
    else:
        known = set(state.get(cfg["known_key"], []))
        session_file = _find_new_session_file(cfg["glob"], known, timeout=15)
        if not session_file:
            # 새 파일 없음 → 가장 최근 수정된 파일로 fallback
            candidates = list(Path.home().glob(cfg["glob"]))
            session_file = max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None
        if not session_file:
            return {"error": f"{target} 세션 파일을 찾을 수 없습니다."}
        state[cfg["file_key"]] = str(session_file)
        _write_state(state)
        state[cfg["file_key"]] = str(session_file)
        _write_state(state)

    if not session_file.exists():
        return {"error": f"세션 파일이 없습니다: {session_file}"}

    ai_types = cfg["ai_types"]
    # known_count: 메시지 전송 직전 count (처음이면 현재 count로 초기화)
    # 단, 방금 보낸 메시지에 대한 응답을 기다려야 하므로 현재 count 기준
    known_count = state.get(cfg["count_key"], len(_read_ai_messages(session_file, ai_types)))
    response = _wait_for_new_message(session_file, ai_types, known_count, timeout)

    if response:
        state[cfg["count_key"]] = len(_read_ai_messages(session_file, ai_types))
        _write_state(state)
        return {"response": response, "target": target, "chars": len(response)}
    return {"error": f"{target} 응답 타임아웃 ({timeout}초)"}


def tool_collab_status() -> dict:
    state = _read_state()
    return {
        "active": bool(state.get("claude_pane") or state.get("gemini_pane")),
        "claude_pane": state.get("claude_pane", "-"),
        "gemini_pane": state.get("gemini_pane", "-"),
        "claude_session": Path(state["claude_session_file"]).name
            if state.get("claude_session_file") else "미탐지",
        "gemini_session": Path(state["gemini_session_file"]).name
            if state.get("gemini_session_file") else "미탐지",
    }


# ── MCP Protocol (JSON-RPC 2.0 over stdio) ───────────────────────────────────

TOOLS = [
    {
        "name": "collab_ask",
        "description": (
            "온디맨드 협업: Gemini CLI 패널을 자동으로 생성하고, 메시지를 전송하고, "
            "응답이 완료되면 텍스트를 반환합니다. "
            "별도 설정 없이 바로 사용 가능합니다. "
            "Gemini와 소통할 때는 이 도구만 사용하세요. "
            "bash로 gemini를 직접 실행하거나 API를 호출하지 마세요. "
            "keep_pane=true로 설정하면 응답 후에도 패널이 유지됩니다."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool": {
                    "type": "string",
                    "enum": ["gemini", "claude"],
                    "description": "실행할 AI 도구",
                },
                "message": {
                    "type": "string",
                    "description": "전달할 메시지 (코드 리뷰 요청, 질문 등)",
                },
                "keep_pane": {
                    "type": "boolean",
                    "default": False,
                    "description": "true면 응답 후 패널 유지, false면 자동 종료",
                },
                "work_dir": {
                    "type": "string",
                    "description": "작업 디렉터리 (기본값: 현재 디렉터리)",
                },
            },
            "required": ["tool", "message"],
        },
    },
    {
        "name": "collab_send",
        "description": (
            "Gemini CLI가 현재 하단 tmux 패널에서 실행 중입니다. "
            "이 도구를 호출하면 해당 패널에 메시지를 직접 붙여넣어 전송합니다. "
            "Playwright, API 키, curl, bash로 gemini를 실행하거나 찾을 필요가 전혀 없습니다. "
            "이 도구만 사용하면 됩니다. "
            "전송 후 반드시 collab_wait(target='gemini')를 호출해 응답을 받으세요."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "enum": ["claude", "gemini"],
                    "description": "메시지를 보낼 대상 AI",
                },
                "message": {
                    "type": "string",
                    "description": "전달할 메시지 (역할 설명 + 작업 내용 포함 권장)",
                },
            },
            "required": ["target", "message"],
        },
    },
    {
        "name": "collab_wait",
        "description": (
            "collab_send 후 Gemini CLI 패널의 응답이 완료될 때까지 대기하고 텍스트를 반환합니다. "
            "반드시 collab_send 호출 직후에 사용하세요. "
            "이 도구가 Gemini의 응답을 자동으로 감지해 반환하므로 "
            "화면을 직접 읽거나 다른 방법을 쓸 필요가 없습니다."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "enum": ["claude", "gemini"],
                    "description": "응답을 기다릴 대상 AI",
                },
                "timeout": {
                    "type": "integer",
                    "default": 120,
                    "description": "최대 대기 시간(초), 기본 120",
                },
            },
            "required": ["target"],
        },
    },
    {
        "name": "collab_status",
        "description": (
            "현재 협업 세션 상태를 확인합니다. "
            "어떤 패널이 활성화됐는지, 세션 파일이 탐지됐는지 확인합니다."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _handle(req: dict) -> dict | None:
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, msg):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": msg}}

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "collab-mcp", "version": "1.0.0"},
        })

    if method in ("notifications/initialized", "initialized"):
        return None  # notification — no response

    if method == "tools/list":
        return ok({"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        try:
            if name == "collab_ask":
                result = tool_collab_ask(
                    args["tool"], args["message"],
                    bool(args.get("keep_pane", False)),
                    args.get("work_dir", ""),
                )
            elif name == "collab_send":
                result = tool_collab_send(args["target"], args["message"])
            elif name == "collab_wait":
                result = tool_collab_wait(args["target"], int(args.get("timeout", 120)))
            elif name == "collab_status":
                result = tool_collab_status()
            else:
                return err(-32601, f"Unknown tool: {name}")
            return ok({"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]})
        except Exception as e:
            return err(-32603, str(e))

    return err(-32601, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = _handle(req)
        if resp is not None:
            print(json.dumps(resp, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
