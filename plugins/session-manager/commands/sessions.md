---
description: Claude Code 세션 목록 조회 및 관리
---

# Claude 세션 관리

사용자 요청: $ARGUMENTS

## 동작 방식

`session_manager.py --claude-mode`를 실행하여 세션 목록을 텍스트로 출력합니다.

## 특수 액션

**install** 요청인 경우 (`$ARGUMENTS`가 "install"):

실행:
python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py install

설치 완료 후 결과를 사용자에게 알려주세요.

## 일반 조회

`$ARGUMENTS`를 다음 규칙으로 변환하여 실행:

| 요청 | 실행 |
|------|------|
| (없음) | `python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py --claude-mode` |
| `--stats` 또는 "통계" | `python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py --stats` |
| 프로젝트명 키워드 | `python3 ${CLAUDE_PLUGIN_ROOT}/session_manager.py --claude-mode --filter "키워드"` |

## 출력 후

- 세션 목록을 보여준 뒤, 사용자가 특정 세션 ID나 이름을 언급하면 `claude --resume <sessionId>` 명령어를 안내합니다.
- 삭제 요청은 터미널에서 `claude-sessions` 도구를 사용하도록 안내합니다.
