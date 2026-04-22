# Cross-Session Context Injection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** cs fzf 브라우저에서 Ctrl+M으로 다른 세션의 compact 요약을 생성해 대상 Claude pane에 주입한다.

**Architecture:** session_manager.py 단일 파일에 3개 함수(`extract_messages_for_summary`, `get_or_generate_summary`, `fzf_inject_context`)와 보조 함수(`fzf_select_target`)를 추가한다. 요약은 `claude -p`로 생성하고 `~/.claude/session-summaries/{session_id}.json`에 캐시한다. 주입은 `tmux load-buffer` + `tmux paste-buffer`로 수행한다.

**Tech Stack:** Python 3.12, tmux 3.4+, fzf, claude CLI (`-p` 플래그)

---

## 파일 구조

| 파일 | 역할 |
|------|------|
| `plugins/session-manager/session_manager.py` | 모든 신규 함수 추가, args 확장, fzf 바인딩 추가 |
| `plugins/session-manager/.claude-plugin/plugin.json` | version → `2.1.0` |
| `.claude-plugin/marketplace.json` | version → `2.1.0` |

신규 함수 삽입 위치 (session_manager.py):
- `SUMMARY_CACHE_DIR` 상수 — line 17 이후 (기존 상수들 다음)
- `extract_messages_for_summary()` — `parse_jsonl_session()` 바로 앞 (line 19 앞)
- `get_or_generate_summary()` — `extract_messages_for_summary()` 바로 다음
- `fzf_select_target()` — `get_tmux_open_sessions()` 바로 앞 (line 302 앞)
- `fzf_inject_context()` — `fzf_select_target()` 바로 다음
- args + handler — 기존 `--fzf-action` 핸들러 패턴과 동일한 위치 (line 1401 근처)

---

## Task 1: 메시지 추출 함수 + 캐시 상수

**Files:**
- Modify: `plugins/session-manager/session_manager.py:13-18`

- [ ] **Step 1: `SUMMARY_CACHE_DIR` 상수 추가**

`VERSION = "2.0.9"` 바로 아래(line 13 다음)에 추가:

```python
SUMMARY_CACHE_DIR = Path.home() / ".claude" / "session-summaries"
```

- [ ] **Step 2: `extract_messages_for_summary` 함수 작성**

`parse_jsonl_session` 함수(line 19) 바로 앞에 삽입:

```python
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
```

- [ ] **Step 3: 수동 검증**

```bash
cd /home/seoji/local/claude-plugins/plugins/session-manager
python3 - <<'EOF'
import sys; sys.argv = ['x']
from session_manager import extract_messages_for_summary
import glob, os
# 가장 최근 세션 파일 찾기
files = sorted(glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True), key=os.path.getmtime, reverse=True)
if files:
    result = extract_messages_for_summary(files[0], max_messages=5)
    print("=== 추출 결과 (최대 5개) ===")
    print(result[:500])
    print("=== OK ===" if result else "=== EMPTY (정상일 수도 있음) ===")
EOF
```

Expected: 메시지 몇 줄이 "사용자: ..." / "Claude: ..." 형식으로 출력됨.

- [ ] **Step 4: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: session-manager - extract_messages_for_summary 추가"
```

---

## Task 2: 요약 생성 + 캐시 함수

**Files:**
- Modify: `plugins/session-manager/session_manager.py` (Task 1에서 삽입한 위치 바로 다음)

- [ ] **Step 1: `get_or_generate_summary` 함수 작성**

`extract_messages_for_summary` 함수 바로 다음에 삽입:

```python
def get_or_generate_summary(session: dict) -> str:
    """세션 요약 반환. 캐시 유효하면 캐시, 아니면 claude -p로 생성 후 캐시 저장."""
    session_id = session.get("sessionId", "")
    full_path = session.get("fullPath", "")
    current_mtime: int = session.get("fileMtime", 0)

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

    try:
        cache_path.write_text(
            json.dumps({"mtime": current_mtime, "summary": summary}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        pass

    return summary
```

- [ ] **Step 2: 캐시 저장/로드 수동 검증**

```bash
python3 - <<'EOF'
import sys, json, os, glob
sys.argv = ['x']
from session_manager import get_or_generate_summary, load_all_sessions
sessions = load_all_sessions()
if not sessions:
    print("세션 없음")
    sys.exit(0)
# 가장 짧은 세션 (빠른 테스트용)
s = min(sessions, key=lambda x: x.get("messageCount", 999))
print(f"테스트 세션: {s.get('summary','')[:40]} ({s.get('messageCount',0)}msgs)")
summary = get_or_generate_summary(s)
print("=== 요약 ===")
print(summary[:300])
# 캐시 재확인
cache = json.loads(open(os.path.expanduser(f"~/.claude/session-summaries/{s['sessionId']}.json")).read())
print(f"\n=== 캐시 저장됨: mtime={cache['mtime']} ===")
EOF
```

Expected: 요약 텍스트 출력 후 "캐시 저장됨" 메시지.

- [ ] **Step 3: 캐시 히트 검증 (두 번째 호출)**

```bash
python3 - <<'EOF'
import sys, time
sys.argv = ['x']
from session_manager import get_or_generate_summary, load_all_sessions
sessions = load_all_sessions()
s = min(sessions, key=lambda x: x.get("messageCount", 999))
t0 = time.time()
summary = get_or_generate_summary(s)
elapsed = time.time() - t0
print(f"소요 시간: {elapsed:.2f}초")
print("캐시 히트 성공" if elapsed < 1.0 else "캐시 미스 (예상치 못한 상황)")
EOF
```

Expected: `소요 시간: 0.0x초` (캐시 히트, 즉시 반환).

- [ ] **Step 4: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: session-manager - get_or_generate_summary + 캐시 로직 추가"
```

---

## Task 3: 대상 선택 fzf + 주입 핸들러

**Files:**
- Modify: `plugins/session-manager/session_manager.py` (`get_tmux_open_sessions` 함수 앞)

- [ ] **Step 1: `fzf_select_target` 함수 작성**

`get_tmux_open_sessions` 함수(line 302) 바로 앞에 삽입:

```python
def fzf_select_target(sessions: list[dict], slot_ids: set[str]) -> str | None:
    """전체 세션 목록 fzf로 보여주고 선택된 session_id 반환. 취소 시 None."""
    lines = []
    for s in sessions:
        sid = s.get("sessionId", "")
        indicator = "\x1b[32m[열림]\x1b[0m" if sid in slot_ids else "\x1b[90m[닫힘]\x1b[0m"
        date = s.get("modified", "")[:10]
        project = s.get("projectPath", "?").split("/")[-1]
        summary = get_display_summary(s)[:50]
        lines.append(f"{indicator} {date}  {project:<20}  {summary}  {sid}")

    result = subprocess.run(
        [
            "fzf",
            "--ansi",
            "--layout=reverse",
            "--prompt=주입할 세션 선택> ",
            "--header=Enter:선택  Esc:취소",
            "--with-nth=1..-2",
        ],
        input="\n".join(lines),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip().split()[-1]
```

- [ ] **Step 2: `fzf_inject_context` 함수 작성**

`fzf_select_target` 바로 다음에 삽입:

```python
def fzf_inject_context(source_session_id: str, sessions_cache_path: str) -> None:
    """Ctrl+M: 소스 세션 compact 요약을 대상 Claude pane에 주입."""
    sessions: list[dict] = []
    if sessions_cache_path:
        try:
            sessions = json.loads(Path(sessions_cache_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if not sessions:
        sessions = load_all_sessions()

    source = next((s for s in sessions if s.get("sessionId") == source_session_id), None)
    if not source:
        sys.stderr.write("\n  소스 세션을 찾을 수 없습니다.\n")
        sys.stderr.flush()
        return

    slot_ids, _ = get_tmux_open_sessions()
    target_id = fzf_select_target(sessions, slot_ids)
    if not target_id:
        return

    if target_id == source_session_id:
        sys.stderr.write("\n  소스와 대상이 동일합니다.\n")
        sys.stderr.flush()
        return

    # 대상이 닫혀 있으면 먼저 오픈
    if target_id not in slot_ids:
        sys.stderr.write("\n  대상 세션 오픈 중...\n")
        sys.stderr.flush()
        tmux_split_open(target_id, sessions_cache_path)

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

    # tmux paste-buffer로 주입 (Enter 없음 — 사용자가 확인 후 전송)
    subprocess.run(["tmux", "load-buffer", "-"], input=formatted, text=True)
    subprocess.run(["tmux", "paste-buffer", "-t", target_pane_id])

    sys.stderr.write("\n  컨텍스트 주입 완료.\n")
    sys.stderr.flush()
```

- [ ] **Step 3: 문법 검증**

```bash
python3 -c "import sys; sys.argv=['x']; import session_manager; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: session-manager - fzf_select_target + fzf_inject_context 추가"
```

---

## Task 4: Args 등록 + fzf 키바인딩 + 헤더 업데이트

**Files:**
- Modify: `plugins/session-manager/session_manager.py` (args 파서 및 `run_fzf_tmux`)

- [ ] **Step 1: `--fzf-inject-context` 인수 추가**

기존 `--fzf-action` 인수 줄(line ~1401) 바로 다음에 추가:

```python
    parser.add_argument("--fzf-inject-context", metavar="SESSION_ID", help=argparse.SUPPRESS)
```

- [ ] **Step 2: 핸들러 등록**

기존 `if args.fzf_action:` 블록 바로 앞에 삽입:

```python
    if args.fzf_inject_context:
        fzf_inject_context(args.fzf_inject_context, args.sessions_cache or "")
        return
```

- [ ] **Step 3: `run_fzf_tmux` 헤더에 `Ctrl-M` 항목 추가**

기존 header 문자열을 다음으로 교체:

```python
    header = (
        "Enter:세션열기  Ctrl-S:화면분할  Ctrl-N:새세션  Ctrl-P:미리보기토글\n"
        "Tab:다중선택  Ctrl-D:삭제(다중)  Ctrl-T:제목편집  Ctrl-R:정렬토글  "
        "Ctrl-M:컨텍스트주입  Ctrl-Z:detach  Ctrl-Q:종료"
    )
```

- [ ] **Step 4: `run_fzf_tmux`에 `ctrl-m` fzf 바인딩 추가**

기존 `"--bind=ctrl-r:reload({_toggle_sort})"` 줄 바로 다음에 추가:

```python
            # ctrl-m: 소스 세션 요약을 대상 pane에 주입
            (
                f"--bind=ctrl-m:execute("
                f"python3 {script_path} --fzf-inject-context {{-1}}"
                f" --sessions-cache {cache_file})"
                f"+reload({_reload_with_cache})"
            ),
```

- [ ] **Step 5: 문법 + 인수 파싱 검증**

```bash
python3 session_manager.py --help 2>&1 | grep -v SUPPRESS | head -20
python3 -c "
import sys; sys.argv = ['x', '--fzf-inject-context', 'dummy-id']
# argparse가 문제없이 파싱되는지만 확인
import session_manager
print('args parse OK')
" 2>&1 | head -5
```

Expected: 도움말 출력 + `args parse OK` (dummy-id로 실제 실행 시 "소스 세션을 찾을 수 없습니다" 출력되면 정상).

- [ ] **Step 6: 커밋**

```bash
git add plugins/session-manager/session_manager.py
git commit -m "feat: session-manager - Ctrl+M 컨텍스트 주입 fzf 바인딩 추가"
```

---

## Task 5: 버전 업 + 로컬 설치 + 푸시

**Files:**
- Modify: `plugins/session-manager/session_manager.py:13`
- Modify: `plugins/session-manager/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: VERSION 변경**

`session_manager.py` line 13:

```python
VERSION = "2.1.0"
```

- [ ] **Step 2: plugin.json 버전 변경**

`plugins/session-manager/.claude-plugin/plugin.json`:

```json
"version": "2.1.0"
```

- [ ] **Step 3: marketplace.json 버전 변경**

`.claude-plugin/marketplace.json`의 session-manager 항목:

```json
"version": "2.1.0"
```

- [ ] **Step 4: 로컬 설치**

```bash
python3 /home/seoji/local/claude-plugins/plugins/session-manager/session_manager.py install
```

Expected:
```
[설치 완료]
  /home/seoji/.local/bin/cs -> ...session_manager.py
```

- [ ] **Step 5: 버전 확인**

```bash
python3 /home/seoji/local/claude-plugins/plugins/session-manager/session_manager.py --version 2>/dev/null || \
python3 -c "import sys; sys.argv=['x']; import importlib.util; spec=importlib.util.spec_from_file_location('sm','/home/seoji/local/claude-plugins/plugins/session-manager/session_manager.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(m.VERSION)"
```

Expected: `2.1.0`

- [ ] **Step 6: 최종 커밋**

```bash
git add plugins/session-manager/session_manager.py \
        plugins/session-manager/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json
git commit -m "feat: session-manager v2.1.0 - 세션 간 컨텍스트 주입 (Ctrl+M)"
```

- [ ] **Step 7: SOL GitLab 푸시**

```bash
git push origin main
```

Expected: `main -> main` 성공 메시지.

- [ ] **Step 8: 개인 GitHub 푸시**

```bash
cd /tmp && rm -rf jhseo-plugin && git clone git@github.com:JiHyeongSeo/jhseo-plugin.git
cd /tmp/jhseo-plugin
cp /home/seoji/local/claude-plugins/plugins/session-manager/session_manager.py plugins/session-manager/session_manager.py
cp /home/seoji/local/claude-plugins/plugins/session-manager/.claude-plugin/plugin.json plugins/session-manager/.claude-plugin/plugin.json
git add -A
git commit -m "feat: session-manager v2.1.0 - 세션 간 컨텍스트 주입 (Ctrl+M)"
git push origin main
```

Expected: `main -> main` 성공 메시지.

---

## 스펙 커버리지 체크

| 스펙 요구사항 | 구현 태스크 |
|---|---|
| Ctrl+M 키바인딩 | Task 4 Step 4 |
| 소스: 하이라이트된 세션 | Task 4 (fzf `{-1}` 사용) |
| 대상: 전체 세션 목록 fzf | Task 3 `fzf_select_target` |
| [열림]/[닫힘] 인디케이터 | Task 3 Step 1 |
| [닫힘] 선택 시 세션 오픈 후 주입 | Task 3 Step 2 (`tmux_split_open` 호출) |
| compact 수준 요약 (`claude -p`) | Task 2 |
| 캐시 (mtime 기반) | Task 2 |
| Enter 없이 주입 | Task 3 (`paste-buffer`) |
| 소스==대상 경고 | Task 3 Step 2 |
| JSONL 없음 처리 | Task 2 (`extract_messages_for_summary` OSError) |
| `claude -p` 실패 처리 | Task 2 (TimeoutExpired, FileNotFoundError) |
| v2.1.0 버전 업 | Task 5 |
