# 회의록 템플릿

회의 안건, 논의 내용, 결정사항, 후속 조치를 기록하는 템플릿

## 1. 문서 목적

회의에서 논의한 안건, 결정 사항, 후속 조치를 체계적으로 기록합니다. 참석하지 못한 팀원도 회의 내용을 파악할 수 있고, Action Item 추적을 통해 후속 조치가 누락되지 않도록 합니다.

### 제목 규칙

```
(YYYY/MM/DD) [회의록] 제목
```

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 회의 정보 | 필수 | 일시, 참석자, 장소/온라인 여부를 table 블록으로 정리 |
| 2 | 안건 | 필수 | 회의 안건을 numbered_list_item으로 나열 |
| 3 | 논의 내용 | 필수 | 안건별 heading_2 소제목 + 논의 내용 기술 |
| 4 | 결정 사항 | 필수 | callout(ℹ️, blue_background) 안에 numbered_list_item으로 정리 |
| 5 | Action Items | 선택 | to_do 블록으로 담당자+기한 포함 |
| 6 | 다음 회의 일정 | 선택 | paragraph로 다음 회의 일정 표시 |

## 3. 섹션별 작성 가이드

### 회의 정보
- **이모지:** 📋
- **블록:** table (키-값 형태, 2열)
- **포함 정보:** 일시, 참석자, 장소(오프라인) 또는 회의 링크(온라인), 불참자
- **작성 팁:** 참석자는 이름 나열. 불참자가 있다면 별도 기재

### 안건
- **이모지:** 📄
- **블록:** numbered_list_item
- **포함 정보:** 회의에서 다룰 주제 목록
- **작성 팁:** 회의 전 미리 작성하여 공유하면 효율적

### 논의 내용
- **이모지:** 💬
- **블록:** heading_2 소제목 + paragraph/bulleted_list_item
- **포함 정보:** 안건별 논의 요약, 주요 의견, 쟁점
- **작성 팁:** 안건 번호에 맞춰 heading_2 소제목으로 구분. 발언자를 명시하면 맥락 파악에 도움

### 결정 사항
- **이모지:** ✅
- **블록:** callout (icon: ℹ️, color: blue_background) + numbered_list_item (children)
- **포함 정보:** 최종 결정 내용, 결정 근거 (필요 시)
- **작성 팁:** 결정된 사항만 명확하게 기록. 미결 사항은 Action Items로 이동

### Action Items (선택)
- **이모지:** 📌
- **블록:** to_do (checked: false)
- **포함 정보:** 할 일, 담당자, 기한
- **작성 팁:** 각 항목에 담당자와 기한을 반드시 포함

### 다음 회의 일정 (선택)
- **이모지:** 📅
- **블록:** paragraph
- **포함 정보:** 다음 회의 일시, 주제
- **작성 팁:** 정기 회의라면 주기도 함께 기록

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) [회의록] 회의 주제` 형식 |
| 요약 (callout 💡) | 항상 | 문서 최상단에 3줄 이내 회의 요약 (핵심 결정사항 중심) |
| table_of_contents | 항상 | 요약 아래에 TOC 블록 삽입 |

## 5. 완성 예시 (Notion Block JSON)

```json
[
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "💡"},
      "color": "green_background",
      "rich_text": [{"type": "text", "text": {"content": "Q1 스프린트 회고 및 Q2 계획 논의"}}]
    }
  },
  {"type": "table_of_contents", "table_of_contents": {"color": "default"}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📋 회의 정보"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "table",
    "table": {
      "table_width": 2,
      "has_column_header": false,
      "has_row_header": false,
      "children": [
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "일시"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "2026/03/28 14:00~15:00"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "장소"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "회의실 A / Zoom"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "참석자"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "김철수, 이영희, 박지민"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "불참자"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "정민수 (휴가)"}}]]}}
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📄 안건"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "Q1 스프린트 회고"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "Q2 목표 설정"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "스프린트 주기 변경 논의"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "💬 논의 내용"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "heading_2",
    "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Q1 스프린트 회고"}}]}
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "목표 대비 80% 달성. 일정 지연의 주요 원인은 외부 API 연동 작업의 의존성 문제로 확인되었습니다."}}]
    }
  },
  {
    "type": "heading_2",
    "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Q2 목표 설정"}}]}
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "텍스트 탐지 v2 출시, 모니터링 대시보드 구축을 Q2 핵심 목표로 논의하였습니다."}}]
    }
  },
  {
    "type": "heading_2",
    "heading_2": {"rich_text": [{"type": "text", "text": {"content": "스프린트 주기 변경 논의"}}]}
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "2주 스프린트에서 3주 스프린트로 변경 시 장단점을 논의. 외부 의존성이 많은 현재 상황에서 3주가 더 적합하다는 의견이 다수였습니다."}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "✅ 결정 사항"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "ℹ️"},
      "color": "blue_background",
      "rich_text": [{"type": "text", "text": {"content": "1. 스프린트 주기를 2주에서 3주로 변경\n2. Q2 핵심 목표: 텍스트 탐지 v2 출시, 모니터링 대시보드 구축"}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📌 Action Items"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "후속 조치가 필요한 항목입니다. 담당자와 기한을 확인하세요."}}]
    }
  },
  {"type": "to_do", "to_do": {"checked": false, "rich_text": [{"type": "text", "text": {"content": "스프린트 보드 설정 변경 (담당: 김철수, 기한: 2026-04-01)"}}]}},
  {"type": "to_do", "to_do": {"checked": false, "rich_text": [{"type": "text", "text": {"content": "Q2 로드맵 문서 작성 (담당: 이영희, 기한: 2026-04-03)"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📅 다음 회의 일정"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "2026/04/04 14:00 - Q2 첫 번째 스프린트 킥오프"}}]
    }
  }
]
```
