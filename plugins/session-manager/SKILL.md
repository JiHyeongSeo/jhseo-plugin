---
name: session-manager
description: AI 세션 브라우저. Claude/Gemini 세션 탐색, tmux 멀티슬롯, fzf 검색, resume/삭제. "세션", "sessions", "resume", "세션 관리" 키워드에서 활성화
---

# Session Manager (cs)

Claude/Gemini 세션을 프로젝트별로 탐색하고 관리하는 플러그인.
`cs` 명령어로 tmux 멀티슬롯 패널 + fzf 검색 인터페이스를 제공합니다.

## 설치

처음 한 번 Claude에서 실행:
```
/session-manager:sessions install
```
설치 시 `collab MCP`도 자동 등록됩니다.

## 터미널 사용법

```bash
cs              # tmux 멀티슬롯 + fzf 브라우저 실행
cs --stats      # 세션 통계 요약
cs --version    # 버전 확인
```

## fzf 단축키

| 키 | 동작 |
|---|---|
| `Enter` | 선택한 세션을 오른쪽 슬롯에서 resume |
| `Ctrl+S` | 선택한 세션을 새 슬롯(화면 분할)으로 resume |
| `Ctrl+N` | 새 세션 시작 (디렉터리 + 툴 선택) |
| `Ctrl+F` | 홈 디렉터리 파일 검색 후 에디터 열기 |
| `Ctrl+X` | 세션 컨텍스트 주입 (다른 Claude 패널에 요약 전달) |
| `Tab` | 다중 선택 |
| `Ctrl+D` | 선택한 세션 삭제 (Tab 다중 선택 가능) |
| `Ctrl+T` | 세션 제목 편집 |
| `Ctrl+R` | 정렬 토글 (날짜순 ↔ 프로젝트순) |
| `Ctrl+P` | 미리보기 토글 |
| `Ctrl+Z` | 브라우저 detach (tmux 세션 유지) |
| `Ctrl+Q` | 브라우저 완전 종료 |

## 세션 배지

| 배지 | 의미 |
|---|---|
| `[C]` | Claude Code 세션 |
| `[G]` | Gemini CLI 세션 |
| `[D]` | Claude+Gemini 협업 페어 세션 |
| `●` (녹색) | 현재 열린 슬롯 |
| `●` (노란색) | 백그라운드 세션 |

## 의존성

- Python 3.10+
- tmux 2.1+
- fzf 0.38.0+
- rich (`pip install rich`)
