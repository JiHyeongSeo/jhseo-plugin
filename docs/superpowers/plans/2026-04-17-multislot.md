# cs 멀티슬롯 오른쪽 패널 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** cs 세션 브라우저의 오른쪽 패널을 최대 2개의 슬롯(위/아래)으로 나눠 두 Claude 세션을 동시에 표시한다.

**Architecture:** 상태 파일 구조를 `{"active": str, "background": [...]}` 에서 `{"slots": [{"session_id", "pane_id"}], "background": [...]}` 로 변경한다. tmux pane_id (`%숫자`)로 슬롯을 추적해 pane 인덱스 재정렬에도 안전하게 동작한다. Enter는 슬롯 수에 따라 바로 열기/교체/선택 프롬프트로 동작하고, Ctrl+S는 두 번째 슬롯을 아래에 추가한다.

**Tech Stack:** Python 3.10+, tmux, fzf, pytest

---

## 파일 구조

수정 파일 하나:
- `plugins/session-manager/session_manager.py` — 모든 변경이 여기에 집중됨
- `plugins/session-manager/tests/test_session_manager.py` — 새 함수 테스트 추가

---

## Task 1: 상태 구조 변경 + pane ID 헬퍼 함수

**Files:**
- Modify: `plugins/session-manager/session_manager.py:231-275`
- Test: `plugins/session-manager/tests/test_session_manager.py`

- [ ] **Step 1: 테스트 작성 (실패 확인용)**

```python
# test_session_manager.py 하단에 추가
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
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
cd plugins/session-manager
python3 -m pytest tests/test_session_manager.py::TestGetAllPaneIds tests/test_session_manager.py::TestReadStateNewFormat -v
```

Expected: FAIL — `_get_all_pane_ids` 함수 없음

- [ ] **Step 3: `_read_state` default 변경 + `_get_all_pane_ids` 추가**

`session_manager.py` 의 `_read_state` / `_write_state` 블록 (라인 234-242)을 아래로 교체:

```python
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
    """fzf pane(window 0의 index 0 pane) ID 반환. 실패 시 '0.0' 대체값."""
    result = subprocess.run(
        ["tmux", "list-panes", "-t", f"{tmux_session}:0",
         "-F", "#{pane_id} #{pane_index}"],
        capture_output=True, text=True,
    )
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
    for line in win_result.stdout.strip().split("\n"):
        parts = line.strip().split(" ", 1)
        if len(parts) == 2 and parts[1] == session_id:
            return parts[0]
    return None
```

- [ ] **Step 4: `run_tmux_layout`의 상태 초기화 라인 변경**

라인 약 857 (`_write_state({"active": "", "background": []})`) 를:

```python
_write_state({"slots": [], "background": []})
```

- [ ] **Step 5: 테스트 실행 → 통과 확인**

```bash
python3 -m pytest tests/test_session_manager.py::TestGetAllPaneIds tests/test_session_manager.py::TestReadStateNewFormat -v
```

Expected: PASS

- [ ] **Step 6: 전체 테스트 통과 확인**

```bash
python3 -m pytest tests/ -q
```

Expected: 37 + 새 테스트 모두 PASS

- [ ] **Step 7: 커밋**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/tests/test_session_manager.py
git commit -m "refactor: 상태 파일 slots 배열 구조 + pane ID 헬퍼 함수 (v2.0.0)"
```

---

## Task 2: `get_tmux_open_sessions` + `format_session_line` 리팩터

**Files:**
- Modify: `plugins/session-manager/session_manager.py:245-294`
- Test: `plugins/session-manager/tests/test_session_manager.py`

- [ ] **Step 1: 테스트 작성**

```python
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
        state_file.write_text(json.dumps({
            "slots": [],
            "background": ["sess-c"],
        }))
        monkeypatch.setattr(session_manager, "_STATE_FILE", state_file)
        fake, _ = self._make_run(pane_ids="%10\n", window_names="0\nsess-c\n")
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
        # ANSI 제거 후 마지막 토큰이 session_id
        import re
        plain = re.sub(r"\x1b\[[0-9;]*m", "", line)
        assert plain.split()[-1] == "abc-444"
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
python3 -m pytest tests/test_session_manager.py::TestGetTmuxOpenSessionsNewFormat tests/test_session_manager.py::TestFormatSessionLineNewSignature -v
```

Expected: FAIL

- [ ] **Step 3: `get_tmux_open_sessions` 교체**

라인 245-275를 아래로 교체:

```python
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
```

- [ ] **Step 4: `format_session_line` 시그니처 변경**

라인 278-294를 아래로 교체:

```python
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
```

- [ ] **Step 5: 호출부 업데이트 — `run_fzf_tmux()`**

`run_fzf_tmux()` 안의 아래 두 라인을:
```python
active_id, bg_ids = get_tmux_open_sessions()
lines = [format_session_line(s, active_id=active_id, bg_ids=bg_ids) for s in sessions]
```

아래로 변경:
```python
slot_ids, bg_ids = get_tmux_open_sessions()
lines = [format_session_line(s, slot_ids=slot_ids, bg_ids=bg_ids) for s in sessions]
```

- [ ] **Step 6: 호출부 업데이트 — `--fzf-list-lines` 핸들러**

`main()` 의 `if args.fzf_list_lines:` 블록 안의:
```python
active_id, bg_ids = get_tmux_open_sessions()
for s in sessions:
    print(format_session_line(s, active_id=active_id, bg_ids=bg_ids))
```

아래로 변경:
```python
slot_ids, bg_ids = get_tmux_open_sessions()
for s in sessions:
    print(format_session_line(s, slot_ids=slot_ids, bg_ids=bg_ids))
```

- [ ] **Step 7: 기존 `TestFormatSessionLine` 테스트 호환성 확인**

기존 테스트는 `format_session_line(s)` (인자 없이)만 호출하므로 수정 불필요. 실행해서 확인:

```bash
python3 -m pytest tests/test_session_manager.py::TestFormatSessionLine -v
```

Expected: PASS (기존 5개 그대로)

- [ ] **Step 8: 새 테스트 통과 확인**

```bash
python3 -m pytest tests/test_session_manager.py::TestGetTmuxOpenSessionsNewFormat tests/test_session_manager.py::TestFormatSessionLineNewSignature -v
```

Expected: PASS

- [ ] **Step 9: 전체 테스트**

```bash
python3 -m pytest tests/ -q
```

Expected: 모두 PASS

- [ ] **Step 10: 커밋**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/tests/test_session_manager.py
git commit -m "refactor: get_tmux_open_sessions slot_ids 반환 + format_session_line 시그니처 변경"
```

---

## Task 3: `_ask_target_slot` 슬롯 선택 프롬프트

**Files:**
- Modify: `plugins/session-manager/session_manager.py` (`_get_right_width` 함수 앞에 추가)
- Test: `plugins/session-manager/tests/test_session_manager.py`

- [ ] **Step 1: 테스트 작성**

```python
class TestAskTargetSlot:
    def _make_slots(self):
        return [
            {"session_id": "sess-a", "pane_id": "%23"},
            {"session_id": "sess-b", "pane_id": "%24"},
        ]

    def _make_sessions(self):
        return [
            make_session("sess-a", summary="clean-chatbot 로깅 개선"),
            make_session("sess-b", summary="claude-plugins session manager"),
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
        assert "sess-a" in prompts[0] or "clean-chatbot" in prompts[0]
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
python3 -m pytest tests/test_session_manager.py::TestAskTargetSlot -v
```

Expected: FAIL — `_ask_target_slot` 없음

- [ ] **Step 3: `_ask_target_slot` 구현**

`_get_right_width` 함수 바로 위에 추가:

```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python3 -m pytest tests/test_session_manager.py::TestAskTargetSlot -v
```

Expected: PASS (6개)

- [ ] **Step 5: 전체 테스트**

```bash
python3 -m pytest tests/ -q
```

Expected: 모두 PASS

- [ ] **Step 6: 커밋**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/tests/test_session_manager.py
git commit -m "feat: _ask_target_slot 슬롯 선택 프롬프트 함수"
```

---

## Task 4: `tmux_split_open` 리라이트 (Enter 동작)

**Files:**
- Modify: `plugins/session-manager/session_manager.py:629-730`

이 태스크는 tmux 의존성 때문에 단위 테스트 대신 수동 검증으로 확인한다.

- [ ] **Step 1: `tmux_split_open` 전체 교체**

라인 629-730 (`def tmux_split_open` ~ 마지막 `select-pane` 호출)을 아래로 교체:

```python
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
    slots: list[dict] = state.get("slots", [])
    bg_list: list[str] = state.get("background", [])

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
            r = subprocess.run([
                "tmux", "join-pane", "-h",
                "-s", f"{tmux_session}:{bg_window_idx}",
                "-t", fzf_pane,
                "-P", "-F", "#{pane_id}",
            ], capture_output=True, text=True)
            new_pane_id = r.stdout.strip()
            if new_pane_id:
                subprocess.run(["tmux", "resize-pane", "-t", new_pane_id, "-x", str(right_width)])
        else:
            r = subprocess.run([
                "tmux", "split-window", "-h", "-l", str(right_width),
                "-t", fzf_pane, "-c", work_dir,
                "-P", "-F", "#{pane_id}",
                f"claude --resume {session_id}",
            ], capture_output=True, text=True)
            new_pane_id = r.stdout.strip()

    elif target_idx == 0:
        # 위 슬롯 위치 → 남은 아래 슬롯(%ref) 위에 삽입
        ref_pane_id = slots[0]["pane_id"]
        if bg_window_idx is not None:
            r = subprocess.run([
                "tmux", "join-pane", "-v", "-b",
                "-s", f"{tmux_session}:{bg_window_idx}",
                "-t", ref_pane_id,
                "-P", "-F", "#{pane_id}",
            ], capture_output=True, text=True)
        else:
            r = subprocess.run([
                "tmux", "split-window", "-v", "-b",
                "-t", ref_pane_id, "-c", work_dir,
                "-P", "-F", "#{pane_id}",
                f"claude --resume {session_id}",
            ], capture_output=True, text=True)
        new_pane_id = r.stdout.strip()

    else:
        # 아래 슬롯 위치 → 남은 위 슬롯(%ref) 아래에 삽입
        ref_pane_id = slots[0]["pane_id"]
        if bg_window_idx is not None:
            r = subprocess.run([
                "tmux", "join-pane", "-v",
                "-s", f"{tmux_session}:{bg_window_idx}",
                "-t", ref_pane_id,
                "-P", "-F", "#{pane_id}",
            ], capture_output=True, text=True)
        else:
            r = subprocess.run([
                "tmux", "split-window", "-v",
                "-t", ref_pane_id, "-c", work_dir,
                "-P", "-F", "#{pane_id}",
                f"claude --resume {session_id}",
            ], capture_output=True, text=True)
        new_pane_id = r.stdout.strip()

    if not new_pane_id:
        return

    # slots에 새 슬롯 삽입 (위치 유지)
    slots.insert(target_idx, {"session_id": session_id, "pane_id": new_pane_id})
    _write_state({"slots": slots, "background": bg_list})
    subprocess.run(["tmux", "select-pane", "-t", new_pane_id])
```

- [ ] **Step 2: 문법 확인**

```bash
python3 -c "import ast; ast.parse(open('plugins/session-manager/session_manager.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: 전체 테스트**

```bash
python3 -m pytest tests/ -q
```

Expected: 모두 PASS

- [ ] **Step 4: 수동 검증 체크리스트**

`cs` 실행 후 아래 시나리오를 순서대로 확인:

```
[ ] 슬롯 0개 → Enter: 오른쪽에 슬롯 1 생성됨
[ ] 같은 세션 재선택 → Enter: 포커스만 이동 (새 pane 미생성)
[ ] 다른 세션 → Enter: 슬롯 1 교체, 기존 세션은 노랑 dot으로 표시
[ ] 노랑 dot 세션 → Enter: 슬롯 1에 복원 (프로세스 유지 확인)
```

- [ ] **Step 5: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: tmux_split_open 다중슬롯 지원 리라이트"
```

---

## Task 5: `tmux_split_add` (Ctrl+S) + fzf 바인딩 + 버전 업

**Files:**
- Modify: `plugins/session-manager/session_manager.py`

- [ ] **Step 1: `tmux_split_add` 함수 추가**

`tmux_split_open` 함수 바로 뒤에 추가:

```python
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
    slots: list[dict] = state.get("slots", [])
    bg_list: list[str] = state.get("background", [])

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
        r = subprocess.run([
            "tmux", "join-pane", "-v",
            "-s", f"{tmux_session}:{bg_window_idx}",
            "-t", slot0_pane_id,
            "-P", "-F", "#{pane_id}",
        ], capture_output=True, text=True)
    else:
        r = subprocess.run([
            "tmux", "split-window", "-v",
            "-t", slot0_pane_id, "-c", work_dir,
            "-P", "-F", "#{pane_id}",
            f"claude --resume {session_id}",
        ], capture_output=True, text=True)

    new_pane_id = r.stdout.strip()
    if not new_pane_id:
        return

    slots.append({"session_id": session_id, "pane_id": new_pane_id})
    _write_state({"slots": slots, "background": bg_list_new})
    subprocess.run(["tmux", "select-pane", "-t", new_pane_id])
```

- [ ] **Step 2: CLI 인자 `--tmux-split-add` 추가**

`main()` 의 `parser.add_argument("--tmux-split-open", ...)` 라인 바로 뒤에:

```python
parser.add_argument("--tmux-split-add", metavar="SESSION_ID", help=argparse.SUPPRESS)
```

- [ ] **Step 3: `--tmux-split-add` 핸들러 추가**

`if args.tmux_split_open:` 블록 바로 뒤에:

```python
if args.tmux_split_add:
    tmux_split_add(args.tmux_split_add, args.sessions_cache or "")
    return
```

- [ ] **Step 4: `run_fzf_tmux()` — Ctrl+S 바인딩 + 헤더 업데이트**

헤더 변경:
```python
header = (
    "Enter:세션열기  Ctrl-S:화면분할  Ctrl-P:미리보기토글  Ctrl-D:삭제  Ctrl-T:제목편집\n"
    "Ctrl-R:날짜정렬  Ctrl-O:프로젝트정렬  Ctrl-C:백그라운드(detach)  Ctrl-Q:완전종료"
)
```

`--bind=enter:...` 라인 바로 뒤에 Ctrl+S 바인딩 추가:

```python
# ctrl-s: 슬롯 2 추가 (슬롯 1개일 때만 동작)
(
    f"--bind=ctrl-s:execute("
    f"python3 {script_path} --tmux-split-add {{-1}}"
    f" --sessions-cache {cache_file})"
    f"+reload({_reload_with_cache})"
),
```

- [ ] **Step 5: VERSION 업**

```python
VERSION = "2.0.0"
```

- [ ] **Step 6: 문법 확인**

```bash
python3 -c "import ast; ast.parse(open('plugins/session-manager/session_manager.py').read()); print('OK')"
python3 plugins/session-manager/session_manager.py --version
```

Expected:
```
OK
cs 2.0.0
```

- [ ] **Step 7: 전체 테스트**

```bash
python3 -m pytest plugins/session-manager/tests/ -q
```

Expected: 모두 PASS

- [ ] **Step 8: 수동 검증 체크리스트**

```
[ ] 슬롯 1개 상태에서 다른 세션 선택 → Ctrl+S: 아래에 슬롯 2 생성
[ ] 두 세션 모두 초록 dot 표시 확인
[ ] 슬롯 2개 상태에서 Ctrl+S: 아무 반응 없음 (무시)
[ ] 슬롯 0개 상태에서 Ctrl+S: 아무 반응 없음 (무시)
[ ] Enter with 2 slots: 1/2 프롬프트 표시
[ ] 프롬프트에서 1 선택: 위 슬롯 교체, 기존 세션 노랑 dot
[ ] 프롬프트에서 2 선택: 아래 슬롯 교체, 기존 세션 노랑 dot
[ ] 프롬프트에서 잘못된 입력: 아무 것도 안 함
[ ] 슬롯에서 exit: 해당 슬롯 제거, 다음 reload에서 dot 사라짐
[ ] Ctrl+C: detach 후 cs 재진입 → 슬롯 상태 복원 (dot 표시)
```

- [ ] **Step 9: 커밋 + 푸시**

```bash
git add plugins/session-manager/session_manager.py plugins/session-manager/tests/test_session_manager.py
git commit -m "feat: 멀티슬롯 오른쪽 패널 지원 (v2.0.0)

- tmux_split_add: Ctrl+S로 슬롯 2 추가 (위아래 분할)
- tmux_split_open: 슬롯 2개일 때 1/2 선택 프롬프트
- 상태 파일: active → slots 배열 (pane_id 추적)
- 초록 dot: 슬롯에 열린 모든 세션, 노랑 dot: bg 보존 세션"

git push
```
