# 트러블슈팅 기록 템플릿

장애/이슈 발생 시 원인 분석과 해결 과정을 기록하는 템플릿

## 1. 문서 목적

장애나 이슈가 발생했을 때 증상, 원인 분석 과정, 해결 방법, 예방 조치를 체계적으로 기록합니다. 동일한 이슈가 재발했을 때 빠르게 참고할 수 있는 지식 베이스 역할을 합니다.

### 제목 규칙

```
(YYYY/MM/DD) [트러블슈팅] 제목
```

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 요약 | 필수 | callout(⚠️, yellow_background)으로 증상 요약 |
| 2 | 증상 | 필수 | 현상 상세 설명, 발생 시간/환경 정보를 table 블록으로 정리 |
| 3 | 원인 분석 | 필수 | 분석 과정, 로그/에러 메시지를 code 블록으로 포함 + callout(📝) 근본 원인 |
| 4 | 해결 방법 | 필수 | numbered_list_item으로 단계별 해결 절차 기술 |
| 5 | 예방 조치 | 필수 | callout(ℹ️, blue_background)으로 재발 방지 방안 제시 |
| 6 | 타임라인 | 선택 | table 블록으로 시간/이벤트/조치 기록 |
| 7 | 관련 이슈 | 선택 | bulleted_list_item으로 관련 이슈 링크 |
| 8 | 참고 자료 | 선택 | bulleted_list_item으로 관련 문서/링크 목록 |

## 3. 섹션별 작성 가이드

### 요약
- **블록:** callout (icon: ⚠️, color: yellow_background)
- **포함 정보:** 이슈 한 줄 요약, 영향 범위, 심각도
- **작성 팁:** 한 눈에 어떤 이슈인지 파악할 수 있게 간결하게 작성

### 증상
- **이모지:** 🚨
- **블록:** table (발생 정보) + paragraph (상세 설명)
- **포함 정보:** 발생 일시, 발생 환경(서버/서비스), 영향 범위, 심각도, 현상 상세 설명
- **작성 팁:** 재현 조건이 있다면 함께 기록

### 원인 분석
- **이모지:** 🔍
- **블록:** paragraph (분석 과정) + code (로그/에러 메시지) + callout (icon: 📝, color: purple_background) 근본 원인
- **포함 정보:** 분석 과정, 핵심 로그/에러 메시지, 근본 원인(Root Cause)
- **작성 팁:** 분석 과정을 시간 순서대로 기술. 로그는 code 블록으로 가독성 확보

### 해결 방법
- **이모지:** ✅
- **블록:** numbered_list_item
- **포함 정보:** 단계별 해결 절차, 실행한 명령어/설정 변경 내용
- **작성 팁:** 다른 사람이 그대로 따라할 수 있을 정도로 구체적으로 작성

### 예방 조치
- **이모지:** 🛡️
- **블록:** callout (icon: ℹ️, color: blue_background)
- **포함 정보:** 재발 방지를 위한 모니터링/알림 설정, 코드/설정 개선 사항, 프로세스 변경
- **작성 팁:** 실행 가능한 구체적인 조치를 기록

### 타임라인 (선택)
- **이모지:** 🕐
- **블록:** table (3열: 시간, 이벤트, 조치)
- **포함 정보:** 장애 발생부터 완전 복구까지 시간 순서대로 기록

### 관련 이슈 (선택)
- **이모지:** 🔗
- **블록:** bulleted_list_item으로 Jira 이슈 링크

### 참고 자료 (선택)
- **이모지:** 📚
- **블록:** bulleted_list_item으로 관련 문서/링크 목록

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) [트러블슈팅] 이슈 요약` 형식 |
| 요약 (callout ⚠️) | 항상 | 문서 최상단에 3줄 이내 이슈 요약 (트러블슈팅은 ⚠️ 사용) |
| table_of_contents | 항상 | 요약 아래에 TOC 블록 삽입 |

## 5. 완성 예시 (Notion Block JSON)

```json
[
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "⚠️"},
      "color": "yellow_background",
      "rich_text": [
        {"type": "text", "text": {"content": "API 서버 응답 지연 (5초 이상)"}, "annotations": {"bold": true}},
        {"type": "text", "text": {"content": " - 전체 사용자 API 호출에 영향"}}
      ]
    }
  },
  {"type": "table_of_contents", "table_of_contents": {"color": "default"}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🚨 증상"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "이슈 발생 환경과 현상을 정리합니다."}}]
    }
  },
  {
    "type": "table",
    "table": {
      "table_width": 2,
      "has_column_header": false,
      "has_row_header": false,
      "children": [
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "발생 일시"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "2026-03-28 14:30 KST"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "발생 환경"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "Production - API Server (ap-northeast-2)"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "영향 범위"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "전체 사용자 API 호출에 영향"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "심각도"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "Critical"}, "annotations": {"bold": true, "color": "red"}}]]}}
      ]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [
        {"type": "text", "text": {"content": "현상 상세:"}, "annotations": {"bold": true}}
      ]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "API 응답 시간이 평균 200ms에서 5초 이상으로 증가. 모든 엔드포인트에서 동일 현상 발생."}}]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔍 원인 분석"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "이슈의 근본 원인을 분석한 과정과 결과입니다."}}]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "CloudWatch 로그 확인 결과 DB 커넥션 풀 고갈이 확인되었습니다."}}]
    }
  },
  {
    "type": "heading_3",
    "heading_3": {"rich_text": [{"type": "text", "text": {"content": "관련 로그/에러 메시지"}}]}
  },
  {
    "type": "code",
    "code": {
      "language": "plain text",
      "rich_text": [{"type": "text", "text": {"content": "ERROR 2026-03-28 14:30:15 [sqlalchemy.pool] Connection pool exhausted\nERROR 2026-03-28 14:30:15 [uvicorn.error] Connection timeout after 5000ms"}}]
    }
  },
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "📝"},
      "color": "purple_background",
      "rich_text": [
        {"type": "text", "text": {"content": "근본 원인 (Root Cause): "}, "annotations": {"bold": true}},
        {"type": "text", "text": {"content": "DB 커넥션 풀 max_size 설정(5)이 트래픽 대비 너무 낮아 커넥션 고갈 발생"}}
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "✅ 해결 방법"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "이슈를 해결하기 위해 수행한 단계별 절차입니다."}}]
    }
  },
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "긴급 대응: API 서버 재시작으로 임시 복구"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "DB 커넥션 풀 max_size를 5에서 20으로 증가"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "설정 변경 후 스테이징 환경에서 부하 테스트 수행"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "프로덕션 배포 및 모니터링 확인"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🛡️ 예방 조치"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "ℹ️"},
      "color": "blue_background",
      "rich_text": [
        {"type": "text", "text": {"content": "재발 방지를 위한 조치 사항:"}, "annotations": {"bold": true}},
        {"type": "text", "text": {"content": "\n- DB 커넥션 풀 사이즈 모니터링 알림 추가 (80% 임계값)\n- 주간 부하 테스트 자동화 파이프라인 구축\n- 커넥션 풀 설정을 환경변수로 관리하도록 변경"}}
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🕐 타임라인"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "quote",
    "quote": {
      "rich_text": [{"type": "text", "text": {"content": "장애 발생부터 복구까지의 시간 순서 기록입니다."}}]
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
              [{"type": "text", "text": {"content": "시간"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "이벤트"}, "annotations": {"bold": true}}],
              [{"type": "text", "text": {"content": "조치"}, "annotations": {"bold": true}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "14:30"}}],
              [{"type": "text", "text": {"content": "모니터링 알림 발생"}}],
              [{"type": "text", "text": {"content": "담당자 확인 시작"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "14:35"}}],
              [{"type": "text", "text": {"content": "DB 커넥션 풀 고갈 확인"}}],
              [{"type": "text", "text": {"content": "API 서버 재시작"}}]
            ]
          }
        },
        {
          "type": "table_row",
          "table_row": {
            "cells": [
              [{"type": "text", "text": {"content": "14:40"}}],
              [{"type": "text", "text": {"content": "서비스 정상 복구 확인"}}],
              [{"type": "text", "text": {"content": "커넥션 풀 설정 변경 착수"}}]
            ]
          }
        }
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔗 관련 이슈"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "PROJECT-456", "link": {"url": "https://jira.example.com/browse/PROJECT-456"}}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📚 참고 자료"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "AWS RDS 커넥션 관리 가이드", "link": {"url": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html"}}}]}}
]
```
