# Cross-Session Context Injection 설계

## 개요

cs 브라우저(fzf)에서 다른 세션의 컨텍스트를 요약하여 현재 작업 중인 Claude 세션에 주입하는 기능.
세션 간 지식 단절 문제를 해결하고, A 세션에서 작업 시 B 세션의 맥락을 참조할 수 있게 한다.

---

## 사용자 플로우

```
cs 브라우저 (fzf 좌측 pane)
  │
  │  세션 하이라이트 후 Ctrl+M
  ▼
[소스 세션 확정] — 하이라이트된 세션이 참조 대상
  │
  ▼
[두 번째 fzf] — 전체 세션 목록에서 주입 대상 선택
  │   > claude-plugins   session-manager 작업 중   [열림]
  │     text-detection   모델 평가 작업 중          [열림]
  │     another-proj     데이터 분석 논의           [닫힘]
  │
  ├─ [열림] 선택 → 해당 pane에 바로 주입
  └─ [닫힘] 선택 → 세션 오픈 후 주입
  │
  ▼
[요약 생성 / 캐시 확인]
  ├─ 캐시 유효 → 즉시 로드
  └─ 캐시 없음 / 만료 → claude -p로 생성 → 캐시 저장
  │
  ▼
[tmux send-keys] — 대상 pane에 요약 텍스트 주입 (Enter 없음)
```

---

## 컴포넌트 설계

### 1. fzf 키바인딩 — `Ctrl+M`

`run_fzf_tmux` 및 `run_fzf`의 fzf args에 추가:

```
--bind="ctrl-m:execute(python3 {script} --fzf-inject-context {session_id} --sessions-cache {cache_file})"
```

fzf 헤더에 `Ctrl-M:컨텍스트주입` 항목 추가.

### 2. `--fzf-inject-context` 핸들러

**진입점**: `python3 session_manager.py --fzf-inject-context {session_id} --sessions-cache {cache_file}`

처리 순서:
1. `session_id`로 소스 세션 로드
2. `--fzf-select-target` 서브 fzf 실행 → 대상 세션 선택
3. 대상 세션이 닫혀 있으면 `tmux_split_open()` 호출로 먼저 오픈
4. `get_or_generate_summary(source_session)` 호출
5. `tmux send-keys -t {target_pane_id} "{formatted_summary}"` 실행

### 3. `--fzf-select-target` — 대상 선택 fzf

전체 세션 목록을 표시하되 열림/닫힘 상태를 인디케이터로 표시:

```
[열림] 2026-04-22  claude-plugins  session-manager 작업 중
[닫힘] 2026-04-20  text-detection  모델 평가 논의
```

선택 결과로 `session_id` 반환.

### 4. 요약 생성 — `get_or_generate_summary(session)`

**캐시 경로**: `~/.claude/session-summaries/{session_id}.json`

**캐시 포맷**:
```json
{
  "mtime": "2026-04-22T10:30:00+00:00",
  "summary": "..."
}
```

**캐시 유효성**: 저장된 `mtime` == 현재 JSONL 파일의 `mtime` → 유효

**생성 로직**:
```python
# JSONL에서 user/assistant 메시지 추출 (최대 150개)
messages = extract_messages(session["fullPath"], max=150)

prompt = f"""다음 Claude 대화 세션을 compact 요약해줘.
포함할 것: 작업 목표, 주요 결정사항, 완료된 작업, 현재 상태, 중요한 코드/설정/파일 경로.
다음 세션에서 이 요약만 보고 바로 작업을 이어갈 수 있을 정도로 상세하게.

{messages}"""

result = subprocess.run(
    ["claude", "-p", prompt],
    capture_output=True, text=True
)
summary = result.stdout.strip()
```

### 5. 주입 포맷

```
[세션 참조: {제목} / {날짜}]
{요약 내용}
---
```

`tmux send-keys -t {pane_id} "{escaped_text}"` — **Enter 없이** 전송.
사용자가 내용 확인 후 직접 Enter.

---

## 파일 변경 범위

| 파일 | 변경 내용 |
|------|-----------|
| `session_manager.py` | `--fzf-inject-context`, `--fzf-select-target` 핸들러 추가, `get_or_generate_summary()` 함수, fzf 키바인딩 추가, 헤더 업데이트 |
| `.claude-plugin/plugin.json` | version → `2.1.0` |
| `.claude-plugin/marketplace.json` | version → `2.1.0` |

---

## 엣지 케이스

| 상황 | 처리 |
|------|------|
| 소스 == 대상 동일 세션 | 경고 메시지 후 중단 |
| `claude -p` 실패 | stderr 출력, 캐시 저장 안 함 |
| JSONL 파일 없음 | "세션 파일 없음" 메시지 |
| tmux 세션 없음 (no-tmux 모드) | 클립보드 복사 폴백 (xclip/pbcopy) |
| 대상 세션 오픈 실패 | 오픈 실패 메시지 후 중단 |

---

## 버전

- 현재: `2.0.9`
- 이 기능 포함: `2.1.0` (마이너 버전 — 신규 기능)
