---
description: 웹 기반 Plan 리뷰 UI를 엽니다
---

# Interactive Review - Plan Review 모드

Plan(Markdown 파일)을 웹 브라우저에서 GitHub PR 리뷰 스타일로 검토합니다.

## 사용법

1. 리뷰할 Plan을 Markdown 파일로 저장합니다
2. 아래 명령어를 실행합니다:

```bash
python ${CLAUDE_PLUGIN_ROOT}/interactive_review.py plan-review --file /path/to/plan.md
```

3. 브라우저가 열리면 사용자가:
   - Source 탭에서 줄별 `[+]` 버튼으로 코멘트를 남기고
   - Preview 탭에서 렌더링된 Markdown을 확인하고
   - General Comment를 작성한 뒤
   - **Approve** 또는 **Request Changes**를 클릭합니다
4. stdout으로 출력된 JSON 결과를 파싱합니다

## 반환 형식

```json
{
  "status": "approved",
  "comments": [
    {"line": 4, "text": "이 부분 재검토 필요"}
  ],
  "general_comment": "전체적으로 좋습니다"
}
```

- `status`: `"approved"` 또는 `"changes_requested"`
- `comments`: 줄별 코멘트 (줄 번호 오름차순)
- `general_comment`: 전체 의견
