---
name: claude-plugin-for-gemini
description: "Claude Code를 호출하여 협업하는 플러그인. 'Claude에게 물어봐', '리뷰 요청', '검증해줘' 등의 요청 시 Claude를 호출합니다."
---

# Claude Plugin for Gemini

이 플러그인은 Gemini CLI가 Claude Code를 호출하여 복잡한 추론, 코드 리뷰, 또는 상호 검증을 수행할 수 있게 합니다.

## Tools

### claude_ask

Claude에게 메시지와 현재 컨텍스트를 전달하고 응답을 받아옵니다.

**Parameters:**
- `message` (string, required): Claude에게 전달할 질문이나 명령
- `include_context` (boolean, optional, default=true): 현재 작업 중인 파일 및 컨텍스트 포함 여부
- `tool` (string, optional, default="claude"): 실행할 Claude CLI 명령어 (기본: claude)

**Usage Examples:**
- "이 로직의 보안 취약점을 Claude한테 확인해달라고 해줘"
- "Claude에게 현재 코드를 개선할 방법을 물어봐"

## Instructions

1. 사용자가 Claude와의 협업을 요청하면 `claude_ask` 도구를 사용하세요.
2. 이 플러그인은 `agents/` 디렉토리에 정의된 페르소나를 활용할 수 있습니다:
   - **Reviewer (`agents/reviewer.md`)**: 코드 리뷰, 보안 점검, 품질 향상 제안 시 사용. Gemini의 제안에 대한 반대 논거(Red Teaming) 제공.
   - **Debugger (`agents/debugger.md`)**: 버그 추적, 에러 로그 분석, 해결책 탐색 시 사용.
   - **Security (`agents/security.md`)**: 보안 취약점 분석 및 방어적 코딩 가이드 제공.
   - **Performance (`agents/performance.md`)**: 알고리즘 최적화 및 시스템 성능 튜닝 제안.
3. 요청 성격에 맞는 에이전트 지침을 읽고, 해당 지침에 명시된 페르소나와 목적을 `message`의 서두에 포함하여 Claude에게 전달하세요.
4. `include_context`가 true인 경우, 현재 대화 맥락에서 중요한 코드 스니펫이나 파일 경로를 `message`에 함께 요약하여 전달하는 것이 좋습니다.
5. Claude의 응답을 받으면 이를 사용자에게 명확히 전달하고, 필요한 경우 제안된 내용을 바탕으로 추가 작업을 수행하세요.
