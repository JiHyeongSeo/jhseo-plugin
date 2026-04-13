# Architecture Decision Record (ADR) 템플릿

기술 의사결정의 배경, 선택지, 최종 결정과 이유를 기록하는 템플릿

## 1. 문서 목적

기술적 의사결정이 필요한 상황에서 배경, 비교한 선택지, 최종 결정과 근거를 체계적으로 기록합니다. "나중에 왜 이렇게 했지?"라는 질문에 답할 수 있는 의사결정 히스토리를 남기는 것이 핵심 목적입니다.

### 제목 규칙

```
(YYYY/MM/DD) ADR-{번호}: {요약}
```

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 메타데이터 | 필수 | table 블록으로 상태/작성일/결정일/결정자 메타데이터 관리 |
| 2 | 컨텍스트 | 필수 | 왜 이 결정이 필요했는지 배경 설명 |
| 3 | 선택지 | 필수 | 비교 table + heading_3 소제목별 bulleted_list_item으로 각 선택지 상세 설명 |
| 4 | 결정 | 필수 | 최종 선택과 근거, callout(💡) 블록으로 강조 |
| 5 | 결과 | 필수 | 이 결정으로 인한 영향, 후속 작업, callout(📝) 주의사항 |
| 6 | 관련 ADR | 선택 | bulleted_list_item으로 관련 ADR 링크 목록 |
| 7 | 참고 자료 | 선택 | bulleted_list_item으로 외부 참고 자료 링크 |

## 3. 섹션별 작성 가이드

### 메타데이터
- **이모지:** 📋
- **블록:** table (2열: 항목, 내용)
- **포함 정보:** 상태, 작성일, 결정일, 결정자
- **상태 표기:** bold 텍스트 + color annotation으로 구분
  - **제안됨** = yellow
  - **승인됨** = green
  - **폐기됨** = gray
  - **대체됨** = red
- **작성 팁:** ADR의 생명주기를 상태로 관리. 폐기 시 대체 ADR 링크 포함

### 컨텍스트
- **이모지:** 📖
- **블록:** paragraph + bulleted_list_item (제약 조건)
- **포함 정보:** 현재 상황, 문제점/필요성, 제약 조건, 고려해야 할 요구사항
- **작성 팁:** 기술적 배경 지식이 없는 사람도 이해할 수 있게 작성. "왜" 이 결정이 필요한지에 집중

### 선택지
- **이모지:** 🔍
- **블록:** table (비교표: 옵션/장점/단점/비고) + heading_3 소제목 + bulleted_list_item (각 선택지 상세)
- **포함 정보:** 옵션명, 장점, 단점, 비고 (비교 테이블) + 각 옵션을 heading_3 소제목 아래 bulleted_list_item으로 상세 설명
- **작성 팁:** 최소 2개 이상의 선택지를 비교. "아무것도 안 함"도 유효한 선택지

### 결정
- **이모지:** ✅
- **블록:** callout (icon: 💡, color: green_background) 최종 결정 강조 + paragraph (근거)
- **포함 정보:** 최종 선택한 옵션, 선택 근거, 트레이드오프 인지 사항
- **작성 팁:** 결정의 근거를 명확하게 기술. 어떤 트레이드오프를 감수했는지도 언급

### 결과
- **이모지:** 📊
- **블록:** bulleted_list_item (변경 사항) + numbered_list_item (후속 작업) + callout (icon: 📝, color: purple_background) 주의사항
- **포함 정보:** 이 결정으로 인해 변경되는 사항, 필요한 후속 작업, 예상되는 리스크
- **작성 팁:** 구체적인 후속 작업과 담당자를 명시하면 실행력이 높아짐

### 관련 ADR (선택)
- **이모지:** 🔗
- **블록:** bulleted_list_item으로 링크 목록 구성

### 참고 자료 (선택)
- **이모지:** 📚
- **블록:** bulleted_list_item으로 링크 목록 구성

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) ADR-{번호}: {결정 사항 한 줄 요약}` 형식 |
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
      "rich_text": [{"type": "text", "text": {"content": "DB를 MySQL 5.7에서 PostgreSQL 16으로 마이그레이션하기로 결정"}}]
    }
  },
  {"type": "table_of_contents", "table_of_contents": {"color": "default"}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📋 메타데이터"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "table",
    "table": {
      "table_width": 2,
      "has_column_header": false,
      "has_row_header": false,
      "children": [
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "상태"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "승인됨"}, "annotations": {"bold": true, "color": "green"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "작성일"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "2026-03-20"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "결정일"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "2026-03-25"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "결정자"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "김철수, 이영희"}}]]}}
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📖 컨텍스트"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "이 결정이 필요하게 된 배경과 현재 상황을 설명합니다."}}]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "현재 MySQL 5.7을 사용 중이나 2023년 10월 EOL이 도래하여 DB 마이그레이션이 필요합니다. 또한 JSON 데이터 처리 요구사항이 증가하고 있어 이를 고려한 DB 선택이 필요합니다."}}]
    }
  },
  {
    "type": "heading_3",
    "heading_3": {"rich_text": [{"type": "text", "text": {"content": "제약 조건"}}]}
  },
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "다운타임 최소화 (30분 이내)"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "기존 ORM(SQLAlchemy) 호환성 유지"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔍 선택지"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "검토한 선택지를 비교합니다."}}]
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
              [{"type": "text", "text": {"content": "옵션"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "장점"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "단점"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "비고"}, "annotations": {"bold": true}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "PostgreSQL 16"}}],
              [{"type": "text", "text": {"content": "JSON 지원 우수, 확장성"}}],
              [{"type": "text", "text": {"content": "팀 학습 곡선"}}],
              [{"type": "text", "text": {"content": "커뮤니티 활발"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "MySQL 8.0"}}],
              [{"type": "text", "text": {"content": "팀 경험 풍부, 운영 안정성"}}],
              [{"type": "text", "text": {"content": "JSON 지원 제한적"}}],
              [{"type": "text", "text": {"content": "기존 DB 업그레이드"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "Aurora MySQL 3"}}],
              [{"type": "text", "text": {"content": "AWS 관리형, 고가용성"}}],
              [{"type": "text", "text": {"content": "비용 높음, 벤더 종속"}}],
              [{"type": "text", "text": {"content": "MySQL 8.0 호환"}}]
            ]
          }
        }
      ]
    }
  },
  {
    "type": "heading_3",
    "heading_3": {"rich_text": [{"type": "text", "text": {"content": "옵션 1: PostgreSQL 16"}}]}
  },
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "JSONB 네이티브 지원으로 복잡한 JSON 쿼리 성능 우수"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "파티셔닝, 병렬 쿼리 등 대용량 데이터 처리에 강점"}}]}},
  {
    "type": "heading_3",
    "heading_3": {"rich_text": [{"type": "text", "text": {"content": "옵션 2: MySQL 8.0"}}]}
  },
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "기존 MySQL 5.7에서 업그레이드 경로가 단순"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "팀 전체가 MySQL 운영 경험 보유"}}]}},
  {
    "type": "heading_3",
    "heading_3": {"rich_text": [{"type": "text", "text": {"content": "옵션 3: Aurora MySQL 3"}}]}
  },
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "AWS 관리형으로 운영 부담 감소"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "비용이 RDS 대비 약 2배로 예산 초과 우려"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "✅ 결정"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "💡"},
      "color": "green_background",
      "rich_text": [
        {"type": "text", "text": {"content": "최종 결정: PostgreSQL 16으로 마이그레이션"}, "annotations": {"bold": true}}
      ]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [
        {"type": "text", "text": {"content": "선택 근거:"}, "annotations": {"bold": true}}
      ]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "JSON 데이터 처리 요구사항이 높고 장기적 확장성을 고려하여 PostgreSQL 16을 선택했습니다."}}]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [
        {"type": "text", "text": {"content": "감수하는 트레이드오프:"}, "annotations": {"bold": true}}
      ]
    }
  },
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "팀원 교육에 2주 소요 예상"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "마이그레이션 기간 동안 일부 기능 제한"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📊 결과"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "이 결정으로 인한 영향과 후속 작업을 정리합니다."}}]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [
        {"type": "text", "text": {"content": "변경 사항:"}, "annotations": {"bold": true}}
      ]
    }
  },
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "ORM 쿼리 일부 수정 필요 (MySQL 전용 구문 제거)"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "CI/CD 파이프라인의 DB 테스트 환경 변경"}}]}},
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [
        {"type": "text", "text": {"content": "후속 작업:"}, "annotations": {"bold": true}}
      ]
    }
  },
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "마이그레이션 스크립트 작성 (담당: 김철수, 기한: 4/10)"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "팀원 PostgreSQL 교육 진행 (담당: 이영희, 기한: 4/15)"}}]}},
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "📝"},
      "color": "purple_background",
      "rich_text": [
        {"type": "text", "text": {"content": "주의: "}, "annotations": {"bold": true}},
        {"type": "text", "text": {"content": "마이그레이션 기간 동안 읽기 전용 모드 운영 필요. 사전에 사용자 공지 필수."}}
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔗 관련 ADR"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "ADR-001: ORM 프레임워크 선택", "link": {"url": "https://example.com/adr-001"}}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📚 참고 자료"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "PostgreSQL 16 공식 문서", "link": {"url": "https://www.postgresql.org/docs/16/"}}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "MySQL to PostgreSQL 마이그레이션 가이드", "link": {"url": "https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL"}}}]}}
]
```
