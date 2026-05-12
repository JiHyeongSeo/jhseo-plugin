---
name: gemini-collab
description: "Claude와의 협업을 위한 도구. 'Claude한테 물어봐', '리뷰 요청', '검증해줘' 등의 요청 시 Claude를 호출하여 응답을 가져옵니다."
---

# Gemini-Claude Collaboration Skill

이 스킬은 Gemini CLI가 Claude Code를 호출하여 협업할 수 있게 합니다.

## Tools

### collab_ask

Claude에게 메시지(코드 리뷰, 질문 등)를 보내고 그 응답을 받아옵니다. `claude -p` 방식을 사용하여 1회성으로 호출합니다.

**Parameters:**
- `message` (string, required): Claude에게 전달할 내용
- `tool` (string, optional, default="claude"): 실행할 도구 이름
- `work_dir` (string, optional): 작업을 수행할 디렉토리

**Usage Examples:**
- "이 코드를 Claude한테 리뷰받아줘"
- "Gemini가 작성한 내용에 대해 Claude의 의견을 물어봐줘"

## Instructions

1. 사용자가 "Claude에게 물어봐", "검증해줘", "리뷰해줘" 등 Claude와의 협업이 필요한 요청을 하면 `collab_ask` 도구를 사용하세요.
2. `message`에는 현재 컨텍스트, 작성한 코드, 그리고 Claude가 수행해야 할 구체적인 역할을 포함하여 상세히 전달하세요.
3. Claude의 응답이 오면 이를 바탕으로 최종 결과를 사용자에게 보고하거나 필요한 수정을 진행하세요.
