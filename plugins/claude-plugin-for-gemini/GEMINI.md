# Claude Plugin for Gemini Instructions

이 파일은 Gemini가 `claude-plugin-for-gemini` 스킬을 사용하여 Claude와 협업할 때 지켜야 할 내부 지침입니다.

## 핵심 원칙
1. **상호 보완**: Gemini는 빠른 컨텍스트 파악과 파일 조작에 능숙하고, Claude(via Claude Code)는 깊이 있는 추론과 복잡한 리팩토링 설계에 강점이 있습니다. 이 장점을 극대화하도록 작업을 분담하세요.
2. **명확한 페르소나**: `agents/` 폴더의 정의를 참고하여 Claude에게 명확한 역할을 부여하세요. "그냥 물어보는 것"보다 "시니어 엔지니어로서 리뷰해달라고 하는 것"이 훨씬 좋은 결과를 냅니다.
3. **최소한의 컨텍스트**: Claude CLI 호출 시 불필요하게 거대한 텍스트를 보내면 비용과 시간이 증가합니다. `include_context=true`를 사용하되, `message`에는 현재 문제와 직접 관련된 코드 섹션을 요약해서 포함하세요.

## 워크플로우 예시
- **버그 수정**:
  1. Gemini가 로컬에서 테스트를 실행하여 에러를 재현합니다.
  2. 에러 로그와 관련 코드를 `agents/debugger.md` 페르소나와 함께 Claude에게 전달합니다 (`claude_ask`).
  3. Claude의 제안을 Gemini가 검토하고 로컬 파일에 적용합니다.
  4. Gemini가 다시 테스트를 돌려 해결되었는지 확인합니다.

- **코드 리뷰**:
  1. 변경된 파일 목록을 확인합니다.
  2. `agents/reviewer.md` 지침에 따라 Claude에게 전체적인 아키텍처와 보안 리뷰를 요청합니다.
  3. Claude가 지적한 사항을 Gemini가 사용자에게 보고하거나 직접 수정합니다.
