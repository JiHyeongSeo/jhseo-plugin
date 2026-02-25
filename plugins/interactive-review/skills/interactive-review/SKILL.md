---
name: interactive-review
description: 웹 기반 인터랙티브 질문/Plan 리뷰 UI. "질문", "interactive", "plan review", "리뷰", "웹으로 질문", "브라우저로" 등의 키워드에서 활성화
---

# Interactive Review 스킬

웹 브라우저 기반 UI로 여러 질문을 한 화면에 표시하거나, Plan을 GitHub PR 리뷰 스타일로 검토하는 스킬입니다.

## 트리거

다음 키워드가 포함된 요청에서 활성화됩니다:
- "interactive review", "인터랙티브 리뷰"
- "웹으로 질문", "브라우저로 질문"
- "plan review", "플랜 리뷰", "계획 리뷰"
- 여러 질문을 한꺼번에 물어봐야 할 때
- Plan/설계 문서에 line-by-line 피드백이 필요할 때

## 사용 시점

### Questions 모드
AskUserQuestion 대신 사용하면 좋은 경우:
- 질문이 3개 이상일 때 (한 화면에서 모두 답변 가능)
- 이전 답변을 수정하고 싶을 수 있을 때
- 옵션이 많아 터미널에서 보기 불편할 때

### Plan Review 모드
ExitPlanMode 대신 사용하면 좋은 경우:
- Plan에 줄별 코멘트가 필요할 때
- Approve/Request Changes 같은 명확한 의사결정이 필요할 때
- Markdown Plan을 렌더링해서 보여주고 싶을 때

## API 사용 방법 (Python CLI)

CLI 경로: `${CLAUDE_PLUGIN_ROOT}/interactive_review.py`

### Questions 모드

```bash
python ${CLAUDE_PLUGIN_ROOT}/interactive_review.py questions --data '{"questions": [...]}'
```

또는 JSON이 길 때:
```bash
python ${CLAUDE_PLUGIN_ROOT}/interactive_review.py questions --data-file /path/to/questions.json
```

**입력 데이터 (AskUserQuestion 호환):**
```json
{
  "questions": [
    {
      "question": "기술 스택은?",
      "header": "Tech",
      "options": [
        {"label": "Python", "description": "백엔드 서버"},
        {"label": "TypeScript", "description": "프론트엔드"}
      ],
      "multiSelect": false
    },
    {
      "question": "추가 요구사항이 있나요?",
      "header": "Extra"
    }
  ]
}
```

**타입 자동 추론:**
- `options` 있음 + `multiSelect: false` → 라디오 (단일 선택)
- `options` 있음 + `multiSelect: true` → 체크박스 (복수 선택)
- `options` 없음 → 텍스트 입력 (자유 입력)

**반환 JSON:**
```json
{
  "answers": [
    {"id": "q0", "question": "기술 스택은?", "type": "single_select", "value": "Python"},
    {"id": "q1", "question": "추가 요구사항이 있나요?", "type": "free_text", "value": "실시간 알림 기능"}
  ]
}
```

### Plan Review 모드

```bash
python ${CLAUDE_PLUGIN_ROOT}/interactive_review.py plan-review --file /path/to/plan.md
```

**반환 JSON:**
```json
{
  "status": "approved",
  "comments": [
    {"line": 4, "text": "이 부분 재검토 필요"},
    {"line": 12, "text": "에러 처리 추가 요망"}
  ],
  "general_comment": "전체적으로 좋습니다"
}
```

- `status`: `"approved"` 또는 `"changes_requested"`
- `comments`: 줄별 코멘트 배열 (줄 번호 오름차순)
- `general_comment`: 전체 코멘트

### 공통 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--port` | 서버 포트 (0 = OS 자동 할당) | 0 |
| `--timeout` | 응답 대기 timeout (초) | 1800 (30분) |

timeout 초과 시 `{"error": "timeout"}` 반환.

## 다른 스킬에서 참조하는 방법

Plan을 작성하고 사용자 리뷰를 받고 싶을 때:
1. Plan을 임시 파일에 저장 (예: `/tmp/plan-XXXXX.md`)
2. `plan-review` 모드로 실행
3. 반환된 JSON의 `status`와 `comments`에 따라 Plan 수정 또는 진행

여러 질문을 한꺼번에 물어보고 싶을 때:
1. 질문 JSON 구성 (AskUserQuestion 호환 형식)
2. `questions` 모드로 실행
3. 반환된 `answers` 배열에서 각 질문의 답변 파싱
