# 가이드 문서 템플릿

## 1. 문서 목적

**설치/설정/사용법 안내** 문서를 작성할 때 사용한다.
API 연동 가이드, 도구 사용법, 환경 설정 매뉴얼, SDK 시작 가이드 등 독자가 단계별로 따라할 수 있는 기술 문서에 적합하다.

### 제목 규칙

```
(YYYY/MM/DD) [가이드] 제목
```

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 개요 | 필수 | callout(💡) 블록으로 이 가이드가 다루는 내용과 대상 독자를 요약 |
| 2 | 설치 | 필수 | 설치 명령어나 다운로드 방법을 code 블록으로 제공 |
| 3 | 설정 | 필수 | 환경변수, 설정 파일 등 구성 방법을 code 블록 + callout(ℹ️) 블록으로 안내 |
| 4 | 사용 방법 | 필수 | API 호출, CLI 명령어 등 실제 사용법을 table 또는 code 블록으로 설명 |
| 5 | 참고 자료 | 필수 | 공식 문서, GitLab 저장소 등 관련 링크 |
| 6 | FAQ | 선택 | 자주 묻는 질문을 toggle 블록으로 구성 |
| 7 | 트러블슈팅 | 선택 | 흔한 오류와 해결 방법을 callout(⚠️) 블록으로 안내 |

## 3. 섹션별 작성 가이드

### 개요
- **블록:** callout (icon: 💡, color: green_background)
- **내용:** 이 가이드가 무엇을 설명하는지, 누구를 대상으로 하는지 1~2문장으로 서술
- 사전 요구사항(필요한 권한, 사전 설치 도구 등)이 있으면 함께 언급

### 설치
- **이모지:** 📦
- **블록:** code (language: bash)
- 패키지 매니저별 설치 명령어, 또는 다운로드 링크 제공
- 여러 환경(OS, 언어 버전)이 있으면 각각 별도 code 블록으로 구분

### 설정
- **이모지:** 🔧
- **블록:**
  - quote 블록으로 설정 개요 설명
  - callout (icon: ℹ️, color: blue_background)으로 중요 참고사항 안내
  - code 블록으로 설정 파일 예시 제공 (language: json/yaml/env 등)
- 필수 설정값과 선택 설정값을 구분하여 서술

### 사용 방법
- **이모지:** 📖
- **블록:** 다음 중 내용에 맞는 방식 선택
  - **table:** API endpoint 목록처럼 요청-응답 쌍을 정리할 때
  - **code:** 실행 가능한 코드 예시를 보여줄 때
  - **numbered_list_item:** 단계별 절차를 설명할 때
- quote 블록으로 사용 방법 개요를 먼저 서술한 뒤 상세 내용 배치

### 참고 자료
- **이모지:** 🔗
- **블록:** bulleted_list_item으로 링크 목록 구성

### FAQ (선택)
- **이모지:** ❓
- **블록:** toggle (제목: 질문, 본문: 답변)
- 각 질문을 toggle의 제목으로, 답변을 children 블록으로 구성
- 질문은 독자 관점에서 작성 (예: "API 키는 어디서 발급받나요?")

### 트러블슈팅 (선택)
- **이모지:** 🔥
- **블록:** callout (icon: ⚠️, color: yellow_background)
- 흔히 발생하는 오류 메시지와 해결 방법을 쌍으로 기술
- 오류별로 callout 블록을 분리하거나, 하나의 callout 안에 정리

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) [가이드] 제목` 형식 |
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
      "rich_text": [{"type": "text", "text": {"content": "이 문서는 텍스트탐지 API의 설치 및 설정 방법을 안내합니다."}}]
    }
  },
  {"type": "table_of_contents", "table_of_contents": {"color": "default"}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📋 개요"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "텍스트탐지 API를 프로젝트에 연동하기 위한 설치, 설정, 사용 방법을 설명합니다."}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📦 설치"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "code",
    "code": {
      "language": "bash",
      "rich_text": [{"type": "text", "text": {"content": "pip install engagement-api"}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔧 설정"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "API 연동을 위해 환경변수를 설정해야 합니다."}}]
    }
  },
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "ℹ️"},
      "color": "blue_background",
      "rich_text": [{"type": "text", "text": {"content": "API 키는 관리자에게 문의하여 발급받으세요."}}]
    }
  },
  {
    "type": "heading_3",
    "heading_3": {"rich_text": [{"type": "text", "text": {"content": "설정 예시"}}]}
  },
  {
    "type": "code",
    "code": {
      "language": "json",
      "rich_text": [{"type": "text", "text": {"content": "{\n  \"api_key\": \"your-api-key\",\n  \"base_url\": \"https://api.example.com/v1\",\n  \"timeout\": 30\n}"}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📖 사용 방법"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "다음과 같이 API를 호출합니다."}}]
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
              [{"type": "text", "text": {"content": "요청"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "동작"}, "annotations": {"bold": true}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "POST /api/detect"}}],
              [{"type": "text", "text": {"content": "텍스트 유해성 탐지"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "GET /api/status"}}],
              [{"type": "text", "text": {"content": "서비스 상태 확인"}}]
            ]
          }
        }
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔗 참고 자료"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "GitLab 저장소", "link": {"url": "https://gitlab.com/project/engagement-api"}}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "API 공식 문서", "link": {"url": "https://api.example.com/docs"}}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "❓ FAQ"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "toggle",
    "toggle": {
      "rich_text": [{"type": "text", "text": {"content": "API 키는 어디서 발급받나요?"}}],
      "children": [
        {
          "type": "paragraph",
          "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": "팀 관리자에게 Slack으로 요청하면 발급받을 수 있습니다."}}]
          }
        }
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔥 트러블슈팅"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "⚠️"},
      "color": "yellow_background",
      "rich_text": [
        {"type": "text", "text": {"content": "ConnectionError: Connection refused"}, "annotations": {"bold": true}},
        {"type": "text", "text": {"content": "\nVPN 연결 상태를 확인하세요. 사내 네트워크에서만 접근 가능합니다."}}
      ]
    }
  }
]
```
