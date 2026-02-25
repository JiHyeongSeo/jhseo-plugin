---
description: 웹 기반 인터랙티브 질문 UI를 엽니다
---

# Interactive Review - 질문 모드

사용자에게 여러 질문을 웹 브라우저 UI로 한꺼번에 보여주고 답변을 받습니다.

## 사용법

1. 질문 데이터를 AskUserQuestion 호환 JSON 형식으로 구성합니다
2. JSON이 짧으면 `--data`로, 길면 임시 파일에 저장 후 `--data-file`로 전달합니다
3. 아래 명령어를 실행합니다:

```bash
python ${CLAUDE_PLUGIN_ROOT}/interactive_review.py questions --data '{"questions": [{"question": "질문 내용", "header": "Label", "options": [{"label": "A", "description": "설명"}], "multiSelect": false}]}'
```

또는 파일로:
```bash
python ${CLAUDE_PLUGIN_ROOT}/interactive_review.py questions --data-file /tmp/questions.json
```

4. 브라우저가 열리면 사용자가 답변을 작성하고 Submit을 누릅니다
5. stdout으로 출력된 JSON 결과를 파싱합니다

## 반환 형식

```json
{
  "answers": [
    {"id": "q0", "question": "질문 내용", "type": "single_select", "value": "A"}
  ]
}
```

`type`은 `single_select`, `multi_select`, `free_text` 중 하나입니다.
