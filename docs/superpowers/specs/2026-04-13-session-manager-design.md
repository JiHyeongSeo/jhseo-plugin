# Session Manager Plugin — Design Spec

**Date:** 2026-04-13  
**Status:** Approved

---

## Overview

Claude Code의 `claude resume` 세션 탐색 경험을 개선하는 플러그인.  
총 22개 프로젝트, 40개 세션이 쌓이면서 목록 탐색 및 관리가 불편해진 문제를 해결한다.

두 가지 인터페이스를 제공한다:
- **터미널 도구** (`claude-sessions`): fzf 기반 인터랙티브 피커
- **Claude 슬래시 커맨드** (`/sessions`): 대화 안에서 세션 목록 확인

---

## Architecture

```
plugins/session-manager/
├── .claude-plugin/
│   └── plugin.json
├── session_manager.py      # 핵심 로직 (터미널 + Claude 모드 공유)
├── commands/
│   └── sessions.md         # /sessions 슬래시 커맨드 정의
└── SKILL.md
```

`session_manager.py` 하나가 두 모드로 동작한다:
- **기본 모드**: fzf 인터랙티브 피커 (터미널 직접 실행)
- **`--claude-mode`**: 텍스트 출력 (Claude가 실행)

데이터 소스: `~/.claude/projects/*/sessions-index.json`

---

## Terminal Tool (`claude-sessions`)

### 설치 위치
`~/.local/bin/claude-sessions` (symlink)

### 실행 모드

| 커맨드 | 동작 |
|--------|------|
| `claude-sessions` | fzf 인터랙티브 피커 (기본) |
| `claude-sessions --list` | rich 트리 출력 (fzf 없이) |
| `claude-sessions --stats` | 전체 통계 요약 |
| `claude-sessions --clean` | 30일 이상 지난 세션 인터랙티브 정리 |

### 기본 실행 흐름
1. `~/.claude/projects/*/sessions-index.json` 읽기
2. 각 세션을 `"<project> | <date> | <summary>"` 형태의 한 줄로 변환 → fzf 입력으로 전달
3. 퍼지 검색: 프로젝트명, summary, firstPrompt 대상
4. 세션 선택 후 액션:
   - `r` Resume → `cd <projectPath> && claude resume <sessionId>`
   - `d` Delete → 확인 후 `.jsonl` 삭제 + `sessions-index.json` 업데이트
   - `v` View → 상세 정보 출력 (summary, 날짜, 메시지 수, 첫 프롬프트)

### fzf 미설치 시
자동으로 `--list` 모드로 폴백, 설치 안내 메시지 표시

### 트리 출력 예시
```
[/home/seoji/local/claude-plugins]  11 sessions
  ├─ 2026-04-12  drawio-notion 플러그인 마켓플레이스 등록   [main]   6 msgs
  ├─ 2026-03-15  confluence 플러그인 수정                  [main]  12 msgs
  └─ ...

[/home/seoji/clean-chatbot]  8 sessions
  ├─ ...
```

---

## Claude Plugin (`/sessions`)

### 커맨드 정의 (`commands/sessions.md`)
Claude에게 `session_manager.py --claude-mode` 실행을 지시하는 마크다운 커맨드.

### 사용 예시
```
/sessions                   # 전체 프로젝트별 세션 목록
/sessions clean-chatbot     # 특정 프로젝트 필터링
/sessions --stats           # 통계만 출력
```

### 출력 형태
```
## Claude Sessions (총 40개, 22개 프로젝트)

### /home/seoji/local/claude-plugins (11개)
- 2026-04-12  drawio-notion 플러그인 마켓플레이스 등록  [main]  6msgs
- 2026-03-15  confluence 플러그인 수정                 [main]  12msgs

### /home/seoji/clean-chatbot (8개)
  ...
```

인터랙션 없이 텍스트만 출력. 원하는 세션 ID를 Claude에게 전달하면 resume 안내 제공.

---

## Installation

플러그인 설치 후 Claude 대화에서 1회 실행:
```
/sessions install
```
Claude가 `session_manager.py`를 `~/.local/bin/claude-sessions`에 심링크하고 실행 권한을 부여한다.  
`~/.local/bin`이 PATH에 없으면 추가 안내를 출력한다.

---

## Data Model

`sessions-index.json` 엔트리 필드:

| 필드 | 용도 |
|------|------|
| `sessionId` | resume/delete 대상 ID |
| `summary` | 세션 요약 (표시 + 검색) |
| `firstPrompt` | 첫 프롬프트 (검색) |
| `created` / `modified` | 날짜 표시 및 정렬 |
| `gitBranch` | 브랜치 표시 |
| `messageCount` | 메시지 수 표시 |
| `projectPath` | 프로젝트별 그룹핑 |
| `fullPath` | `.jsonl` 삭제 대상 경로 |

---

## Out of Scope

- 세션 내용 전체 검색 (`.jsonl` 파싱) — 성능 문제로 제외
- GUI / 웹 인터페이스
- 세션 간 병합 또는 내보내기
