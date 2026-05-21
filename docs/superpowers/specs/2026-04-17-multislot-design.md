# cs 멀티슬롯 오른쪽 패널 설계

## 개요

Claude Code 세션 브라우저(`cs`)의 오른쪽 패널을 최대 2개의 슬롯으로 분할하여 두 개의 Claude 세션을 동시에 표시할 수 있게 한다.

---

## 핵심 개념

- **슬롯(Slot)**: 오른쪽 패널에 표시되는 각 tmux pane. 최대 2개.
- **슬롯 1 (위)**: 기본 슬롯. `Enter`로 세션을 열거나 교체한다.
- **슬롯 2 (아래)**: 선택적 슬롯. `Ctrl+S`(화면 분할 키)로 생성한다.
- **백그라운드**: `break-pane`으로 보존된 세션. 프로세스는 살아있다.

---

## 레이아웃

```
슬롯 1개일 때:              슬롯 2개일 때:
┌──────────┬────────────┐   ┌──────────┬────────────┐
│          │ claude A 🟢│   │          │ claude A 🟢│
│   fzf    │            │   │   fzf    ├────────────┤
│  브라우저 │            │   │  브라우저 │ claude B 🟢│
└──────────┴────────────┘   └──────────┴────────────┘
```

슬롯 2는 슬롯 1 아래에 세로(vertical) 분할로 추가된다.

---

## 키 바인딩

| 키 | 슬롯 0개 | 슬롯 1개 | 슬롯 2개 |
|---|---|---|---|
| `Enter` | 슬롯 1 생성 후 열기 | 슬롯 1 교체 (기존 → background) | 1/2 텍스트 프롬프트로 선택 |
| `Ctrl+S` | — (무시) | 슬롯 2 위아래 분할 생성 후 열기 | 무시 (이미 분할됨) |
| `Enter` (이미 열린 세션) | — | 해당 슬롯으로 포커스 이동 | 해당 슬롯으로 포커스 이동 |

- `Ctrl+S`는 "화면을 쪼개는 키"로 정의. 슬롯이 이미 2개면 더 쪼갤 게 없으므로 무시. 슬롯 0개일 때도 무시 (Enter로 먼저 슬롯 1을 만들어야 함).
- 슬롯에서 `exit` 또는 Claude 세션 종료 → 해당 슬롯 제거, reload 시 상태 반영.

---

## 슬롯 선택 프롬프트

`Enter` 시 슬롯이 2개이면 `/dev/tty`로 아래 프롬프트를 표시한다.

```
어느 슬롯에 열까요?
1) 위  │ clean-chatbot — 로깅 개선 작업
2) 아래│ claude-plugins — session manager
선택 (1/2):
```

- 숫자 하나 입력으로 선택. 그 외 입력은 취소(아무것도 안 함).
- 선택된 슬롯의 기존 세션은 background로 보존.

---

## fzf 목록 표시 규칙

| 표시 | 의미 |
|---|---|
| `🟢 ●` (초록) | 슬롯에 현재 열린 세션 (슬롯 1 또는 슬롯 2 모두) |
| `🟡 ●` (노랑) | 백그라운드에 보존된 세션 |
| (없음) | 미열린 세션 |

---

## 상태 파일 구조

`/tmp/claude-browser-state.json`

```json
{
  "slots": [
    {"session_id": "uuid_A", "pane_id": "%23"},
    {"session_id": "uuid_B", "pane_id": "%24"}
  ],
  "background": ["uuid_C"]
}
```

- `pane_id`: tmux 고유 pane ID (`%숫자` 형식). 슬롯 추가/삭제 시 인덱스가 재정렬돼도 안전하게 추적.
- 기존 `"active"` 필드는 `"slots"` 배열로 대체.
- 슬롯 순서: index 0 = 위, index 1 = 아래.

---

## 상태 검증 (reload 시)

`get_tmux_open_sessions()` 에서 매 reload마다:

1. 각 slot의 `pane_id`가 tmux에 실제 존재하는지 확인 (`tmux list-panes -F '#{pane_id}'`)
2. 존재하지 않는 slot은 제거
3. `background` 목록도 tmux window name으로 실존 검증

---

## 영향받는 함수 목록

| 함수 | 변경 내용 |
|---|---|
| `_read_state()` / `_write_state()` | `active` → `slots` 배열 구조 |
| `get_tmux_open_sessions()` | 단일 active → slots 전체 반환 |
| `format_session_line()` | `active_id` → `slot_ids: set[str]` |
| `tmux_split_open()` | 슬롯 선택 프롬프트 + 다중 슬롯 관리 |
| `run_fzf_tmux()` | `Ctrl+S` 바인딩 추가 |
| `run_tmux_layout()` | 상태 초기화 시 slots 배열로 |

---

## 새로 추가되는 함수

- `_ask_target_slot(slots, sessions_cache)` → int: 슬롯 선택 프롬프트, 선택된 슬롯 인덱스 반환
- `_get_all_pane_ids(tmux_session)` → set[str]: 현재 tmux window의 모든 pane ID 반환

---

## 스코프 외 (이번 구현에서 제외)

- 슬롯 3개 이상 지원
- 가로 분할 지원 (현재는 세로만)
- 슬롯 간 포커스 전환 단축키 (tmux 기본 단축키로 대체)
