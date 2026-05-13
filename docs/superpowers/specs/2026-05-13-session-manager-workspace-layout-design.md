# session-manager v2.5.0 워크스페이스 레이아웃 설계

## 개요

`cs` 기본 모드를 3-pane 워크스페이스 레이아웃으로 전환한다. 기존에는 fzf 세션 선택 후 우측에 Claude/Gemini 창이 열리는 2-pane 구조였으나, yazi 파일 브라우저 pane을 추가해 파일 탐색·미리보기·편집을 Claude 작업과 동시에 진행할 수 있게 한다.

## 레이아웃

```
┌──────────────────────────────┬──────────────────┐
│  pane 0: fzf 세션목록        │  pane 2:         │
│  (상단 30%, 좌 70%)          │  Claude/Gemini   │
├──────────────────────────────┤  (우 30%,        │
│  pane 1: yazi                │  full height)    │
│  (하단 70%, 좌 70%)          │                  │
│  [parent dir][files][preview]│                  │
└──────────────────────────────┴──────────────────┘
```

### 패널별 역할

| pane | 크기 | 도구 | 역할 |
|------|------|------|------|
| 0 | 좌 70% × 상 30% | fzf | 세션 목록 브라우저 |
| 1 | 좌 70% × 하 70% | yazi | 디렉터리 탐색 + 파일 미리보기 |
| 2 | 우 30% × 100% | shell | Claude/Gemini 세션 |

yazi의 3-컬럼 내부 레이아웃(`parent dir | current files | preview`)이 "디렉터리 트리"와 "파일 미리보기"를 자연스럽게 제공한다.

## tmux 분할 순서

```
new-session (claude-browser)
  → split-window -h -p 30       # 우 30% = pane 2 (Claude/Gemini shell)
  → select-pane 좌
  → split-window -v -p 70       # 하 70% = pane 1 (yazi)
  → pane 0 상단: fzf 실행
  → pane 1 하단: yazi $HOME 실행
  → pane 2 우측: 빈 shell (세션 선택 대기)
```

## 인터랙션

### Enter (세션 선택)

fzf에서 세션 선택 시 두 동작이 동시에 실행된다:

1. **pane 2**: `claude --resume <session_id>` 또는 Gemini 실행
2. **pane 1**: yazi를 해당 세션의 `projectPath`로 이동
   - `tmux send-keys -t {yazi_pane} q ""` → yazi 종료
   - `tmux send-keys -t {yazi_pane} "yazi /project/path" Enter` → 재시작

### yazi 내부 동작 (변경 없음)

- 방향키 탐색 → 파일 미리보기 즉시 갱신 (yazi 네이티브)
- Enter → 에디터(vi 등)로 파일 편집
- `q` → yazi 종료 (pane은 유지, shell 대기 상태)

### 키바인딩 (fzf pane 기준)

| 키 | 동작 |
|----|------|
| Enter | 세션 오픈 (pane 2) + yazi 이동 (pane 1) |
| Ctrl+N | 새 Claude 세션 생성 → pane 2에 오픈 |
| Ctrl+G | lazygit popup (프로젝트 경로 기준) |
| Ctrl+T | 세션 제목 편집 |
| Ctrl+R | 정렬 토글 (date ↔ project) |
| Ctrl+X | 세션 컨텍스트 주입 |
| ~~Ctrl+S~~ | 제거 (slot-add) |
| ~~Ctrl+E~~ | 제거 (yazi popup, yazi가 항상 표시되므로 불필요) |

## 코드 변경 범위

### 제거

| 대상 | 이유 |
|------|------|
| `tmux_split_add()` 함수 | 고정 우측 pane으로 대체 |
| `fzf_select_target()` 함수 | pane 선택 UI 불필요 |
| `_ask_target_slot()` 함수 | pane 선택 UI 불필요 |
| `_get_all_pane_ids()` 함수 | slot 관리 불필요 |
| `_find_bg_window_idx()` 함수 | slot 관리 불필요 |
| state의 `slots` 필드 | slot 상태 관리 불필요 |
| state의 `background` 필드 | background pane 관리 불필요 |
| `--tmux-split-add` CLI 인자 | 대응 함수 제거 |
| fzf `ctrl-s` 바인딩 | 제거 |
| fzf `ctrl-e` 바인딩 | yazi 항상 표시로 불필요 |
| `run_yazi_popup()` 함수 | yazi 항상 표시로 불필요 |

### 수정

| 대상 | 변경 내용 |
|------|-----------|
| `run_tmux_layout()` | 3-pane 구성으로 재작성 |
| `tmux_split_open()` | pane 2 고정 오픈 + pane 1 yazi 이동 추가 |
| `run_fzf_tmux()` | ctrl-s, ctrl-e 바인딩 제거 |
| `tmux_new_session()` | pane 2 고정 오픈으로 단순화 |
| `VERSION` | 2.4.4 → 2.5.0 |

### 신규

| 대상 | 내용 |
|------|------|
| `navigate_yazi(project_path, tmux_session)` | yazi pane에 tmux send-keys로 경로 이동. yazi가 실행 중이면 `q`로 종료 후 재시작, 종료 상태(shell 대기)면 바로 시작 |

## 엣지 케이스

- **Enter 두 번째 세션 선택**: pane 2의 기존 세션을 종료하고 새 세션으로 교체 (`tmux send-keys C-c` + resume)
- **yazi를 사용자가 `q`로 종료**: pane 1은 shell 대기 상태. 다음 세션 선택 시 `navigate_yazi`가 yazi를 재시작
- **projectPath가 없거나 존재하지 않는 경로**: yazi를 `$HOME`에서 시작

## 버전

`2.4.4` → `2.5.0` (major UX 변경)
