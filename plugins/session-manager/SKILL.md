---
name: session-manager
description: Claude Code 세션 브라우저. 프로젝트별 트리 탐색, fzf 검색, resume/삭제 관리. "세션", "세션 목록", "sessions", "resume", "세션 관리" 키워드에서 활성화
---

# Session Manager

Claude Code 세션을 프로젝트별로 탐색하고 관리하는 플러그인입니다.

## 터미널 도구 설치

처음 한 번 Claude에서 실행:
```
/sessions install
```

## 터미널 사용법

```bash
claude-sessions           # fzf 인터랙티브 피커 (기본)
claude-sessions --list    # rich 트리 출력
claude-sessions --stats   # 통계 요약
claude-sessions --clean   # 30일 이상 지난 세션 정리
```

## Claude 슬래시 커맨드

```
/sessions                   # 전체 세션 목록
/sessions clean-chatbot     # 특정 프로젝트 필터
/sessions --stats           # 통계
/sessions install           # 터미널 도구 설치
```

## 의존성

- Python 3.10+
- `rich` (`pip install rich`)
- `fzf` (`sudo apt install fzf` 또는 `brew install fzf`)
