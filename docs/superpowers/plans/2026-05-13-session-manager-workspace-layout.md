# session-manager v2.5.0 워크스페이스 레이아웃 구현 플랜

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `cs` 기본 모드를 3-pane 워크스페이스(fzf 세션목록 | yazi 파일브라우저 | Claude/Gemini)로 전환한다.

**Architecture:** tmux 3-pane 고정 레이아웃. 세션 선택 시 `tmux respawn-pane -k`로 우측 pane을 교체하고, `navigate_yazi()`로 yazi를 프로젝트 경로로 이동. 슬롯/백그라운드 상태 관리 전체 제거, 새 상태 스키마: `{right_session_id, yazi_pane_id, claude_pane_id}`.

**Tech Stack:** Python 3, tmux, fzf, yazi, pytest

---

## 파일 수정 범위

| 파일 | 변경 |
|------|------|
| `plugins/session-manager/session_manager.py` | 함수 제거·수정·신규 추가, VERSION 2.5.0 |
| `plugins/session-manager/.claude-plugin/plugin.json` | version 2.5.0 |
| `plugins/session-manager/tests/test_session_manager.py` | 신규 테스트 추가 |

---

## Task 1: 상태 스키마 변경 + navigate_yazi() 추가

**Files:**
- Modify: `plugins/session-manager/session_manager.py:481-490` (`_read_state`)
- Test: `plugins/session-manager/tests/test_session_manager.py`

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_session_manager.py` 파일 끝에 추가:

```python
class TestNewState:
    def test_read_state_default_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        assert session_manager._read_state() == {}

    def test_write_read_state_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        state = {"right_session_id": "abc", "yazi_pane_id": "%5", "claude_pane_id": "%6"}
        session_manager._write_state(state)
        assert session_manager._read_state() == state


class TestNavigateYazi:
    def test_navigate_valid_path(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        session_manager._write_state({"yazi_pane_id": "%99"})
        calls = []
        monkeypatch.setattr(session_manager.subprocess, "run", lambda *a, **kw: calls.append(a[0]))
        monkeypatch.setattr(session_manager.time, "sleep", lambda _: None)
        session_manager.navigate_yazi(str(tmp_path))
        assert any("q" in c for c in calls)
        assert any(str(tmp_path) in " ".join(c) for c in calls)

    def test_navigate_invalid_path_uses_home(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        session_manager._write_state({"yazi_pane_id": "%99"})
        calls = []
        monkeypatch.setattr(session_manager.subprocess, "run", lambda *a, **kw: calls.append(a[0]))
        monkeypatch.setattr(session_manager.time, "sleep", lambda _: None)
        session_manager.navigate_yazi("/nonexistent/path/xyz")
        home = str(Path.home())
        assert any(home in " ".join(c) for c in calls)

    def test_navigate_no_pane_id_noop(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        session_manager._write_state({})
        calls = []
        monkeypatch.setattr(session_manager.subprocess, "run", lambda *a, **kw: calls.append(a[0]))
        session_manager.navigate_yazi(str(tmp_path))
        assert calls == []
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
cd /home/seoji/jhseo-plugin/plugins/session-manager
python -m pytest tests/test_session_manager.py::TestNewState tests/test_session_manager.py::TestNavigateYazi -v
```

Expected: FAIL (navigate_yazi not defined, _read_state returns old default)

- [ ] **Step 3: `_read_state()` 기본값 변경**

`session_manager.py:485` 수정:

```python
def _read_state() -> dict:
    try:
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
```

- [ ] **Step 4: `navigate_yazi()` 신규 추가**

`run_yazi_popup()` 함수 직전(line ~1097)에 삽입:

```python
def navigate_yazi(project_path: str, tmux_session: str = "claude-browser") -> None:
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
```

- [ ] **Step 5: 테스트 재실행 → 통과 확인**

```bash
python -m pytest tests/test_session_manager.py::TestNewState tests/test_session_manager.py::TestNavigateYazi -v
```

Expected: PASS (5개)

- [ ] **Step 6: 커밋**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/tests/test_session_manager.py
git commit -m "feat: session-manager - 상태 스키마 단순화, navigate_yazi() 추가"
```

---

## Task 2: `get_tmux_open_sessions()` 단순화

**Files:**
- Modify: `plugins/session-manager/session_manager.py:668-697`
- Test: `plugins/session-manager/tests/test_session_manager.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
class TestGetTmuxOpenSessionsNew:
    def test_returns_right_session_from_state(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        session_manager._write_state({"right_session_id": "abc-123"})
        slot_ids, bg_ids = session_manager.get_tmux_open_sessions()
        assert slot_ids == {"abc-123"}
        assert bg_ids == set()

    def test_returns_empty_when_no_right_session(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_manager, "_STATE_FILE", tmp_path / "state.json")
        session_manager._write_state({})
        slot_ids, bg_ids = session_manager.get_tmux_open_sessions()
        assert slot_ids == set()
        assert bg_ids == set()
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
python -m pytest tests/test_session_manager.py::TestGetTmuxOpenSessionsNew -v
```

Expected: FAIL

- [ ] **Step 3: `get_tmux_open_sessions()` 재작성**

`session_manager.py:668-697` 전체 교체:

```python
def get_tmux_open_sessions(tmux_session: str = "claude-browser") -> tuple[set[str], set[str]]:
    """상태 파일에서 우측 pane의 열린 세션 반환."""
    state = _read_state()
    right_session_id = state.get("right_session_id", "")
    slot_ids = {right_session_id} if right_session_id else set()
    return slot_ids, set()
```

- [ ] **Step 4: 테스트 재실행 → 통과 확인**

```bash
python -m pytest tests/test_session_manager.py::TestGetTmuxOpenSessionsNew -v
```

Expected: PASS

- [ ] **Step 5: 커밋**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/tests/test_session_manager.py
git commit -m "refactor: session-manager - get_tmux_open_sessions 단순화"
```

---

## Task 3: `run_tmux_layout()` 3-pane 레이아웃으로 재작성

**Files:**
- Modify: `plugins/session-manager/session_manager.py:1850-1921` (`run_tmux_layout`)

> 이 Task는 tmux 실제 호출이라 자동 테스트 없음. 수동 검증으로 대체.

- [ ] **Step 1: `run_tmux_layout()` 전체 교체**

`session_manager.py:1850` ~ `run_fzf` 이전까지 전체 교체:

```python
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
```

- [ ] **Step 2: 수동 검증**

```bash
# 기존 세션이 있으면 먼저 종료
tmux kill-session -t claude-browser 2>/dev/null; cs
```

3-pane 레이아웃 확인:
- 좌상단: fzf 세션 목록
- 좌하단: yazi (파일 브라우저)
- 우측: 빈 shell

- [ ] **Step 3: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: session-manager - 3-pane 워크스페이스 레이아웃"
```

---

## Task 4: `tmux_split_open()` 재작성

**Files:**
- Modify: `plugins/session-manager/session_manager.py:1337-1481` (`tmux_split_open`)

- [ ] **Step 1: `tmux_split_open()` 전체 교체**

`session_manager.py:1337~1482` 전체를 아래로 교체:

```python
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
    tmux_session = "claude-browser"

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
    navigate_yazi(work_dir, tmux_session)
```

- [ ] **Step 2: 수동 검증**

```bash
# cs 실행 후 세션 선택(Enter)
cs
# Enter로 세션 선택 → 우측에 claude --resume 실행, yazi가 프로젝트 경로로 이동하는지 확인
```

- [ ] **Step 3: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "refactor: session-manager - tmux_split_open 고정 우측 pane + navigate_yazi"
```

---

## Task 5: `tmux_new_session()` 단순화

**Files:**
- Modify: `plugins/session-manager/session_manager.py:1559-1715` (`tmux_new_session`)

- [ ] **Step 1: `tmux_new_session()` 슬롯 관련 코드 제거**

`tmux_new_session()` 함수 내 `if not selected_dir or not Path(selected_dir).is_dir(): return` 이후부터 함수 끝까지를 아래로 교체:

```python
    tmux_session = "claude-browser"
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
    navigate_yazi(selected_dir, tmux_session)

    # Gemini: 세션 파일 생성까지 대기 (최대 5초 폴링)
    if selected_tool == "gemini":
        chats_before = set(GEMINI_DIR.glob("tmp/*/chats/session-*.json"))
        for _ in range(10):
            time.sleep(0.5)
            chats_after = set(GEMINI_DIR.glob("tmp/*/chats/session-*.json"))
            if chats_after - chats_before:
                break
```

> 교체 시작 위치: `tmux_session = "claude-browser"` 줄(현재 line ~1640)부터 함수 끝까지.

- [ ] **Step 2: 수동 검증**

```bash
# cs 실행 후 Ctrl+N → 디렉터리 선택 → 우측 pane에 새 claude 세션 시작 확인
```

- [ ] **Step 3: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "refactor: session-manager - tmux_new_session 슬롯 관리 제거"
```

---

## Task 6: `run_fzf_tmux()` 바인딩 정리

**Files:**
- Modify: `plugins/session-manager/session_manager.py:1717-1848` (`run_fzf_tmux`)

- [ ] **Step 1: header 업데이트**

`session_manager.py:1743-1747` 교체:

```python
    header = (
        "Enter:세션열기  Ctrl-N:새세션  Ctrl-P:미리보기토글\n"
        "Tab:다중선택  Ctrl-D:삭제(다중)  Ctrl-T:제목편집  Ctrl-R:정렬토글\n"
        "Ctrl-X:컨텍스트주입  Ctrl-G:Git현황  Ctrl-Z:detach  Ctrl-Q:종료"
    )
```

- [ ] **Step 2: ctrl-s 바인딩 제거**

`session_manager.py:1795-1801` (ctrl-s 블록) 전체 삭제:

```python
            # ctrl-s: 슬롯 2 추가 (fresh)
            (
                f"--bind=ctrl-s:execute("
                f"python3 {script_path} --tmux-split-add {{-1}}"
                f" --sessions-cache {cache_file})"
                f"+reload({_reload_fresh})"
            ),
```

- [ ] **Step 3: ctrl-e 바인딩 제거**

`session_manager.py` 에서 아래 줄 삭제:

```python
            f"--bind=ctrl-e:execute(python3 {script_path} --yazi-popup {{-1}} --sessions-cache {cache_file})",
```

- [ ] **Step 4: 수동 검증**

```bash
cs
# fzf 헤더에 Ctrl-S, Ctrl-E 없는지 확인
# Ctrl-N, Ctrl-G, Ctrl-T, Ctrl-R, Ctrl-X 동작 확인
```

- [ ] **Step 5: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "refactor: session-manager - fzf ctrl-s, ctrl-e 바인딩 제거"
```

---

## Task 7: 불필요한 함수 및 CLI 인자 제거

**Files:**
- Modify: `plugins/session-manager/session_manager.py`

- [ ] **Step 1: 함수 제거**

각 함수를 `grep -n "^def <함수명>"` 으로 위치 확인 후 해당 `def` 줄부터 다음 `def` 줄 직전까지 삭제:

```bash
grep -n "^def tmux_split_add\|^def fzf_select_target\|^def _ask_target_slot\|^def _get_all_pane_ids\|^def _find_bg_window_idx\|^def _get_right_width\|^def run_yazi_popup" \
  plugins/session-manager/session_manager.py
```

삭제 대상:
- `tmux_split_add()`
- `fzf_select_target()`
- `_ask_target_slot()`
- `_get_all_pane_ids()`
- `_find_bg_window_idx()`
- `_get_right_width()`
- `run_yazi_popup()`

- [ ] **Step 2: CLI 인자 제거**

`main()` 내 아래 항목 삭제:

```python
# 삭제할 add_argument 라인들:
parser.add_argument("--tmux-split-add", metavar="SESSION_ID", help=argparse.SUPPRESS)
parser.add_argument("--yazi-popup", metavar="SESSION_ID", help=argparse.SUPPRESS)
```

```python
# 삭제할 dispatch 블록들:
if args.tmux_split_add:
    tmux_split_add(args.tmux_split_add, args.sessions_cache or "")
    return

# main()의 --yazi-popup dispatch 블록도 삭제
```

- [ ] **Step 3: 전체 테스트 실행**

```bash
python -m pytest tests/test_session_manager.py -v
```

Expected: 기존 테스트 포함 전부 PASS

- [ ] **Step 4: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "refactor: session-manager - 슬롯 관리 함수·CLI 인자 전체 제거"
```

---

## Task 8: VERSION 업데이트 + 재설치

**Files:**
- Modify: `plugins/session-manager/session_manager.py:14`
- Modify: `plugins/session-manager/.claude-plugin/plugin.json`

- [ ] **Step 1: VERSION 업데이트**

`session_manager.py:14`:
```python
VERSION = "2.5.0"
```

`plugins/session-manager/.claude-plugin/plugin.json`:
```json
{
  "name": "session-manager",
  "description": "AI 세션 브라우저. Claude/Gemini 세션 탐색, 멀티슬롯 tmux 패널, fzf 검색, resume/삭제 관리",
  "version": "2.5.0",
  ...
}
```

- [ ] **Step 2: 플러그인 캐시 복사 + cs 재설치**

```bash
INSTALL_DIR="/home/seoji/.claude/plugins/cache/jhseo-plugins/session-manager/2.5.0"
mkdir -p "$INSTALL_DIR"
cp -r /home/seoji/jhseo-plugin/plugins/session-manager/. "$INSTALL_DIR/"
python3 "$INSTALL_DIR/session_manager.py" install
```

Expected:
```
[설치 완료]
  /home/seoji/.local/bin/cs -> .../2.5.0/session_manager.py
[의존성 확인]
  ✓ ...
```

- [ ] **Step 3: installed_plugins.json 업데이트**

`~/.claude/plugins/installed_plugins.json` 의 `session-manager@jhseo-plugins` 블록:
```json
{
  "installPath": "/home/seoji/.claude/plugins/cache/jhseo-plugins/session-manager/2.5.0",
  "version": "2.5.0",
  "lastUpdated": "2026-05-13T12:00:00.000Z"
}
```

- [ ] **Step 4: 최종 통합 검증**

```bash
# 1. 기존 세션 종료
tmux kill-session -t claude-browser 2>/dev/null

# 2. cs 실행 → 3-pane 레이아웃 확인
cs

# 3. 세션 Enter → 우측 claude 오픈 + yazi 이동 확인
# 4. Ctrl+N → 새 세션 생성 확인
# 5. Ctrl+G → lazygit 팝업 확인
# 6. yazi 방향키 탐색 → 파일 미리보기 갱신 확인
```

- [ ] **Step 5: 최종 커밋**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/.claude-plugin/plugin.json
git commit -m "feat: session-manager v2.5.0 - 3-pane 워크스페이스 레이아웃"
```
