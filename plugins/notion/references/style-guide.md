# Notion 문서 스타일 가이드

## 1. 문서 레이아웃 구조

Notion은 블록 기반 에디터이므로 Confluence의 `ac:layout`이 필요 없습니다.
모든 콘텐츠는 블록을 순서대로 배치하여 구성합니다.

### 기본 구조

```json
[
  // 1. 요약 (callout)
  // 2. TOC (table_of_contents)
  // 3. 빈 줄 (paragraph)
  // 4. 섹션 반복: heading_1 → divider → 본문 블록들 → 빈 줄
]
```

### 2단 레이아웃이 필요한 경우

Notion에서는 column_list와 column 블록을 사용합니다:

```json
{
  "type": "column_list",
  "column_list": {
    "children": [
      {
        "type": "column",
        "column": {"children": [/* 왼쪽 블록들 */]}
      },
      {
        "type": "column",
        "column": {"children": [/* 오른쪽 블록들 */]}
      }
    ]
  }
}
```

## 2. 섹션 헤더 스타일

### 표준 패턴: heading_1 + 이모지 + divider

```json
[
  {
    "type": "heading_1",
    "heading_1": {
      "rich_text": [{"type": "text", "text": {"content": "📋 섹션 제목"}}]
    }
  },
  {"type": "divider", "divider": {}}
]
```

### 소제목

```json
{
  "type": "heading_2",
  "heading_2": {
    "rich_text": [{"type": "text", "text": {"content": "소제목"}}]
  }
}
```

### 섹션 간 간격

빈 paragraph 블록으로 구분:

```json
{"type": "paragraph", "paragraph": {"rich_text": []}}
```

### 자주 사용하는 이모지

| 용도 | 이모지 |
|------|--------|
| 개요/정보 | 📋 |
| 문서/변경 | 📄 |
| 설정/톱니 | 🔧 |
| 설치/다운로드 | 📥 |
| 사용자/방법 | 👤 |
| 체크리스트 | ✅ |
| 경고/주의 | ⚠️ |
| 검색/확인 | 🔍 |
| 링크/참고 | 🔗 |
| FAQ/질문 | ❓ |
| 아키텍처 | 🏗️ |

## 3. Callout 블록 (패널 대체)

Confluence의 tip/info/warning/note 패널을 Notion callout으로 대체합니다.

| Confluence 패널 | Notion callout | icon | color |
|---|---|---|---|
| tip (초록) | 요약/팁 | 💡 | green_background |
| info (파랑) | 참고/안내 | ℹ️ | blue_background |
| warning (노랑) | 경고/주의 | ⚠️ | yellow_background |
| note (보라) | 메모/참고 | 📝 | purple_background |

```json
{
  "type": "callout",
  "callout": {
    "icon": {"type": "emoji", "emoji": "💡"},
    "color": "green_background",
    "rich_text": [{"type": "text", "text": {"content": "요약 내용"}}]
  }
}
```

## 4. 테이블

### 기본 테이블

```json
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
            [{"type": "text", "text": {"content": "헤더1"}, "annotations": {"bold": true}}],
            [{"type": "text", "text": {"content": "헤더2"}, "annotations": {"bold": true}}]
          ]
        }
      },
      {
        "type": "table_row",
        "table_row": {
          "cells": [
            [{"type": "text", "text": {"content": "값1"}}],
            [{"type": "text", "text": {"content": "값2"}}]
          ]
        }
      }
    ]
  }
}
```

### 키-값 테이블 (메타데이터)

배포 정보, 회의 정보 등 키-값 형태:

```json
{
  "type": "table",
  "table": {
    "table_width": 2,
    "has_column_header": false,
    "has_row_header": false,
    "children": [
      {
        "type": "table_row",
        "table_row": {
          "cells": [
            [{"type": "text", "text": {"content": "항목명"}, "annotations": {"bold": true}}],
            [{"type": "text", "text": {"content": "값"}}]
          ]
        }
      }
    ]
  }
}
```

## 5. 코드 블록

```json
{
  "type": "code",
  "code": {
    "language": "python",
    "rich_text": [{"type": "text", "text": {"content": "print('hello')"}}]
  }
}
```

주요 language 값: `python`, `javascript`, `bash`, `json`, `yaml`, `sql`, `java`, `go`

## 6. 목록

### 순서 있는 목록

```json
{"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "첫 번째 항목"}}]}}
```

### 순서 없는 목록

```json
{"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "항목"}}]}}
```

### 체크리스트

```json
{"type": "to_do", "to_do": {"checked": false, "rich_text": [{"type": "text", "text": {"content": "할 일 항목"}}]}}
```

## 7. 인용문 (Quote)

섹션 설명이나 인용에 사용:

```json
{
  "type": "quote",
  "quote": {
    "rich_text": [{"type": "text", "text": {"content": "섹션이 다루는 내용을 한 줄로 요약합니다."}}]
  }
}
```

## 8. 토글 (FAQ, 접기/펴기)

Confluence의 expand 매크로 대체:

```json
{
  "type": "toggle",
  "toggle": {
    "rich_text": [{"type": "text", "text": {"content": "API 키는 어디서 발급받나요?"}}],
    "children": [
      {"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "팀 관리자에게 Slack으로 요청하면 발급받을 수 있습니다."}}]}}
    ]
  }
}
```

## 9. 링크

### 인라인 링크

```json
{"type": "text", "text": {"content": "링크 텍스트", "link": {"url": "https://example.com"}}}
```

### 북마크 블록

```json
{"type": "bookmark", "bookmark": {"url": "https://example.com"}}
```

## 10. 텍스트 스타일 (Annotations)

```json
{
  "type": "text",
  "text": {"content": "스타일 텍스트"},
  "annotations": {
    "bold": true,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  }
}
```

### 색상 값

| color | 용도 |
|-------|------|
| `default` | 기본 텍스트 |
| `red` | DEV 환경, 위험/오류 |
| `yellow` | STAGE 환경, 주의 |
| `green` | PRODUCT 환경, 성공 |
| `blue` | 참고, 링크 |
| `gray` | 비활성, 부가 정보 |

## 11. Status 표현

Confluence의 `ac:status` 매크로를 Notion에서는 bold + color annotation으로 표현:

```json
[
  {"type": "text", "text": {"content": "PRODUCT"}, "annotations": {"bold": true, "color": "green"}}
]
```

| 환경 | color | 표시 |
|------|-------|------|
| DEV | red | **DEV** |
| STAGE | yellow | **STAGE** |
| PRODUCT | green | **PRODUCT** |

## 12. Embed 블록

외부 콘텐츠 삽입 (draw.io 다이어그램 등):

```json
{
  "type": "embed",
  "embed": {
    "url": "https://viewer.diagrams.net/?..."
  }
}
```

draw.io 다이어그램 삽입 시에는 drawio-notion 플러그인을 사용하세요.

## 13. 작성 원칙

1. **문장**: 40자 이내
2. **문단**: 3줄 이내
3. **구조**: 숫자/결과 먼저, bullet point 우선
4. **강조**: bold 남발 금지, 핵심 키워드만 강조
5. **간격**: 섹션 사이에 빈 paragraph 블록 하나로 시각적 구분
6. **일관성**: 같은 유형의 정보는 같은 블록 타입으로 표현
