# 아키텍처/설계 문서 템플릿

시스템 구조, 데이터 흐름, 기술 스택을 문서화하는 템플릿

## 1. 문서 목적

새로운 시스템을 구축하거나 기존 시스템의 전체 구조를 문서화할 때 작성합니다. 시스템 아키텍처, 컴포넌트 간 관계, 데이터 흐름, 기술 스택 선택 이유를 한 곳에 정리하여 팀원 간 공유 및 온보딩 자료로 활용합니다.

### 제목 규칙

```
(YYYY/MM/DD) [아키텍처] 제목
```

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 개요 | 필수 | callout(💡) 블록으로 문서 목적 간략 설명 |
| 2 | 시스템 아키텍처 | 필수 | embed 블록으로 draw.io 다이어그램 삽입 (drawio-notion 플러그인 활용) |
| 3 | 컴포넌트 설명 | 필수 | 각 컴포넌트의 역할, 기술스택, 비고를 table 블록으로 정리 |
| 4 | 데이터 흐름 | 필수 | numbered_list_item으로 시간 순서대로 기술 |
| 5 | 기술 스택 | 선택 | 카테고리별 사용 기술, 버전, 용도를 table 블록으로 정리 |
| 6 | 의사결정 기록 | 선택 | heading_3 소제목 + table(pros/cons) + callout(💡) 결정 |
| 7 | 관련 문서 | 선택 | 참고 링크 목록 |

## 3. 섹션별 작성 가이드

### 개요
- **블록:** callout (icon: 💡, color: green_background)
- **포함 정보:** 이 문서가 다루는 시스템 이름, 문서의 목적, 대상 독자
- **작성 팁:** 1~2문장으로 간결하게 작성

### 시스템 아키텍처
- **이모지:** 🏗️
- **블록:** embed (draw.io viewer URL)
- **포함 정보:** 전체 시스템 구성도, 컴포넌트 간 연결 관계, 외부 연동 시스템
- **작성 팁:** drawio-notion 플러그인으로 draw.io XML을 생성하고 viewer.diagrams.net URL로 인코딩하여 embed 블록으로 삽입. quote 블록으로 다이어그램 설명 추가

### 컴포넌트 설명
- **이모지:** 📦
- **블록:** table (4열: 컴포넌트명, 역할, 기술스택, 비고)
- **포함 정보:** 아키텍처 다이어그램에 표시된 모든 컴포넌트의 역할과 기술스택
- **작성 팁:** 다이어그램에 표시된 모든 컴포넌트를 빠짐없이 기술

### 데이터 흐름
- **이모지:** 🔄
- **블록:** numbered_list_item
- **포함 정보:** 요청/응답 흐름, 데이터 변환 과정, 비동기 처리 흐름
- **작성 팁:** 번호를 매겨 시간 순서대로 기술. 복잡한 흐름은 추가 draw.io 다이어그램 사용

### 기술 스택 (선택)
- **이모지:** 🛠️
- **블록:** table (4열: 카테고리, 기술, 버전, 용도)
- **포함 정보:** 주요 의존성 기술만 기록. 마이너 라이브러리는 생략

### 의사결정 기록 (선택)
- **이모지:** 📝
- **블록:** heading_3 소제목 + table(선택지/장점/단점) + callout(💡, green_background) 결정
- **포함 정보:** 결정 배경, 비교한 선택지, 최종 결정 및 이유
- **작성 팁:** 각 결정을 heading_3 소제목으로 구분. 나중에 ADR 문서로 분리할 수도 있음

### 관련 문서 (선택)
- **이모지:** 🔗
- **블록:** bulleted_list_item으로 링크 목록 구성

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) [아키텍처] 시스템명 아키텍처` 형식 |
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
      "rich_text": [{"type": "text", "text": {"content": "이 문서는 텍스트 탐지 시스템의 전체 아키텍처와 구성 요소를 설명합니다."}}]
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
      "rich_text": [{"type": "text", "text": {"content": "텍스트 탐지 시스템의 전체 구조와 각 컴포넌트 간 관계를 설명합니다."}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🏗️ 시스템 아키텍처"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "전체 시스템 구성도입니다. 각 컴포넌트 간 연결 관계와 데이터 흐름을 확인할 수 있습니다."}}]
    }
  },
  {
    "type": "embed",
    "embed": {
      "url": "https://viewer.diagrams.net/?tags=%7B%7D&highlight=0&edit=_blank&layers=1&nav=1#R{encoded_drawio_xml}"
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📦 컴포넌트 설명"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "시스템을 구성하는 각 컴포넌트의 역할과 기술스택을 정리합니다."}}]
    }
  },
  {
    "type": "table",
    "table": {
      "table_width": 4,
      "has_column_header": true,
      "has_row_header": false,
      "children": [
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "컴포넌트명"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "역할"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "기술스택"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "비고"}, "annotations": {"bold": true}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "API Gateway"}}],
              [{"type": "text", "text": {"content": "외부 요청 수신 및 라우팅"}}],
              [{"type": "text", "text": {"content": "Kong Gateway"}}],
              [{"type": "text", "text": {"content": "Rate limiting 적용"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "탐지 서버"}}],
              [{"type": "text", "text": {"content": "텍스트 유해성 분석 및 판정"}}],
              [{"type": "text", "text": {"content": "FastAPI + PyTorch"}}],
              [{"type": "text", "text": {"content": "GPU 인스턴스 사용"}}]
            ]
          }
        }
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔄 데이터 흐름"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "주요 데이터 흐름을 시간 순서대로 설명합니다."}}]
    }
  },
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "클라이언트가 API Gateway에 탐지 요청 전송"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "API Gateway가 인증 확인 후 탐지 서버로 라우팅"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "탐지 서버가 ML 모델로 텍스트 분석 수행"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "분석 결과를 DB에 저장하고 클라이언트에 응답 반환"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🛠️ 기술 스택"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "시스템에서 사용하는 주요 기술 스택입니다."}}]
    }
  },
  {
    "type": "table",
    "table": {
      "table_width": 4,
      "has_column_header": true,
      "has_row_header": false,
      "children": [
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "카테고리"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "기술"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "버전"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "용도"}, "annotations": {"bold": true}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "Backend"}}],
              [{"type": "text", "text": {"content": "FastAPI"}}],
              [{"type": "text", "text": {"content": "0.104.0"}}],
              [{"type": "text", "text": {"content": "REST API 서버"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "Database"}}],
              [{"type": "text", "text": {"content": "PostgreSQL"}}],
              [{"type": "text", "text": {"content": "16"}}],
              [{"type": "text", "text": {"content": "메인 데이터 저장소"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "Infra"}}],
              [{"type": "text", "text": {"content": "AWS ECS Fargate"}}],
              [{"type": "text", "text": {"content": "-"}}],
              [{"type": "text", "text": {"content": "컨테이너 오케스트레이션"}}]
            ]
          }
        }
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📝 의사결정 기록"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "주요 기술 의사결정의 배경과 근거를 기록합니다."}}]
    }
  },
  {
    "type": "heading_3",
    "heading_3": {"rich_text": [{"type": "text", "text": {"content": "DB 선택: PostgreSQL vs MySQL"}}]}
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [
        {"type": "text", "text": {"content": "배경: "}, "annotations": {"bold": true}},
        {"type": "text", "text": {"content": "JSON 데이터 처리 요구사항이 높아 DB 선택이 필요했습니다."}}
      ]
    }
  },
  {
    "type": "table",
    "table": {
      "table_width": 3,
      "has_column_header": true,
      "has_row_header": false,
      "children": [
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "선택지"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "장점"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "단점"}, "annotations": {"bold": true}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "PostgreSQL 16"}}],
              [{"type": "text", "text": {"content": "JSON 지원 우수, 확장성"}}],
              [{"type": "text", "text": {"content": "팀 학습 곡선"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "MySQL 8.0"}}],
              [{"type": "text", "text": {"content": "팀 경험 풍부, 운영 안정성"}}],
              [{"type": "text", "text": {"content": "JSON 지원 제한적"}}]
            ]
          }
        }
      ]
    }
  },
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "💡"},
      "color": "green_background",
      "rich_text": [
        {"type": "text", "text": {"content": "결정: "}, "annotations": {"bold": true}},
        {"type": "text", "text": {"content": "PostgreSQL 16으로 결정. JSON 데이터 처리 요구사항이 높고 장기적 확장성 고려."}}
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔗 관련 문서"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "API 설계 문서", "link": {"url": "https://example.com/api-spec"}}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "배포 가이드", "link": {"url": "https://example.com/deploy-guide"}}}]}}
]
```
