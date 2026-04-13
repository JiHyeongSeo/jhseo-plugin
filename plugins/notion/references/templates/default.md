# 기본 문서 템플릿

## 1. 문서 목적

특정 유형(배포, 가이드 등)에 해당하지 않는 **범용 기본 문서**를 작성할 때 사용한다.

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 요약 | 필수 | callout(💡) 블록으로 문서의 목적과 배경을 1~2문장으로 요약 |
| 2 | TOC | 필수 | table_of_contents 블록 삽입 |
| 3 | 본문 섹션 (1개 이상) | 필수 | 문서 주제에 맞는 제목을 자유롭게 설정. heading_1 + 이모지 + divider 패턴 |
| 4 | 참고 자료 | 선택 | 관련 문서, 외부 링크 등을 목록으로 정리 |

## 3. 섹션별 작성 가이드

### 요약
- **블록:** callout (icon: 💡, color: green_background)
- **내용:** 문서가 다루는 주제와 목적을 간결하게 서술

### 본문 섹션
- **헤더 패턴:** heading_1에 이모지 prefix + divider
- **이모지 선택:** 섹션 성격에 맞는 이모지 사용 (📋 개요, 🔧 설정, 📊 데이터 등)
- **섹션 설명:** 필요 시 quote 블록으로 해당 섹션이 다루는 내용을 한 줄 요약
- **본문 구성:**
  - 비교/목록성 정보는 **table** 블록 사용
  - 절차/순서가 있는 내용은 **numbered_list_item** 블록
  - 나열형 정보는 **bulleted_list_item** 블록
  - 코드가 포함되면 **code** 블록 (language 지정)
- **섹션 간 간격:** 빈 paragraph 블록으로 구분

### 참고 자료
- **이모지:** 🔗
- **형식:** bulleted_list_item 블록으로 링크 목록 구성

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) 제목` 형식 |
| 요약 (callout 💡) | 항상 | 문서 최상단에 3줄 이내 요약 |
| table_of_contents | 항상 | 요약 아래에 TOC 블록 삽입 |

## 5. 완성 예시 (Notion Block JSON)

```json
[
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "💡"},
      "color": "green_background",
      "rich_text": [{"type": "text", "text": {"content": "이 문서는 OO 시스템의 구성과 연동 현황을 설명합니다."}}]
    }
  },
  {"type": "table_of_contents", "table_of_contents": {"color": "default"}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {
      "rich_text": [{"type": "text", "text": {"content": "📋 개요"}}]
    }
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "시스템의 전체 구조와 각 컴포넌트의 역할을 정리합니다."}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {
      "rich_text": [{"type": "text", "text": {"content": "📄 시스템 구성"}}]
    }
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "각 컴포넌트의 역할과 기술 스택을 정리합니다."}}]
    }
  },
  {
    "type": "table",
    "table": {
      "table_width": 2,
      "has_column_header": true,
      "has_row_header": false,
      "children": [
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "항목"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "내용"}, "annotations": {"bold": true}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "API 서버"}}],
              [{"type": "text", "text": {"content": "FastAPI 기반 REST API, ECS Fargate에서 운영"}}]
            ]
          }
        }
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {
      "rich_text": [{"type": "text", "text": {"content": "🔗 참고 자료"}}]
    }
  },
  {"type": "divider", "divider": {}},
  {
    "type": "bulleted_list_item",
    "bulleted_list_item": {
      "rich_text": [{"type": "text", "text": {"content": "시스템 아키텍처 문서", "link": {"url": "https://example.com/architecture"}}}]
    }
  }
]
```
