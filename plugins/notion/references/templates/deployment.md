# 배포 문서 템플릿

## 1. 문서 목적

서비스 **배포/패치 기록**을 남길 때 사용한다.

### 제목 규칙

```
(YYYY/MM/DD) [배포] 배포 개요 한 줄 요약
```

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 배포 정보 | 필수 | 배포 일시, 버전, 환경, 담당자 등 핵심 메타데이터를 table 블록으로 정리 |
| 2 | 변경 사항 | 필수 | 이번 배포에 포함된 변경 내역을 목록으로 나열 |
| 3 | 배포 절차 | 필수 | 배포 단계를 순서대로 numbered_list_item으로 기술 |
| 4 | 롤백 계획 | 필수 | 문제 발생 시 복구 방법을 구체적으로 기술 |
| 5 | 체크리스트 | 필수 | 배포 전/중/후 확인 항목을 to_do 블록으로 구성 |
| 6 | 배포 후 확인 사항 | 필수 | 배포 완료 후 검증 항목 목록 |
| 7 | 이슈 및 해결 | 필수 | 배포 중 발생한 이슈와 해결 방법 |
| 8 | 참고 자료 | 선택 | GitLab MR, Jira 티켓 등 관련 링크 |

## 3. 섹션별 작성 가이드

### 배포 정보
- **블록:** table (2열: 항목, 내용)
- **포함할 항목:** 배포 일시, 배포 버전, 배포 환경, 담당자
- **배포 환경 표기:** bold 텍스트 + color annotation으로 구분
  - **DEV** = red, **STAGE** = yellow, **PRODUCT** = green
- **이모지:** 📋

### 변경 사항
- **블록:** bulleted_list_item
- 각 항목은 "무엇을 변경했는지" 명확하게 서술
- **이모지:** 📄

### 배포 절차
- **블록:** numbered_list_item
- 각 단계는 구체적으로 작성, 명령어는 code 블록으로 감싸기
- **이모지:** ✅

### 롤백 계획
- **블록:** paragraph 또는 numbered_list_item
- 롤백 트리거 조건, 절차, 확인 사항 포함
- **이모지:** ⚠️

### 체크리스트
- **블록:** to_do (checked: false)
- 배포 전/중/후 확인 항목
- **이모지:** ✅

### 배포 후 확인 사항
- **블록:** bulleted_list_item
- API 응답 정상 여부, 로그 모니터링, 성능 지표 등
- **이모지:** 🔍

### 이슈 및 해결
- **블록:** 이슈가 있으면 table 또는 목록, 없으면 "특이사항 없음" paragraph
- **이모지:** ⚠️

### 참고 자료
- **블록:** bulleted_list_item
- **이모지:** 🔗

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) [배포] 제목` 형식 |
| 요약 (callout 💡) | 항상 | 최상단 3줄 이내 요약 |
| table_of_contents | 항상 | 요약 아래에 TOC |

## 5. 완성 예시 (Notion Block JSON)

```json
[
  {
    "type": "callout",
    "callout": {
      "icon": {"type": "emoji", "emoji": "💡"},
      "color": "green_background",
      "rich_text": [{"type": "text", "text": {"content": "금칙어 처리 v2 API 기반 증분 갱신 배포"}}]
    }
  },
  {"type": "table_of_contents", "table_of_contents": {"color": "default"}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📋 배포 정보"}}]}
  },
  {"type": "divider", "divider": {}},
  {
    "type": "table",
    "table": {
      "table_width": 2,
      "has_column_header": false,
      "has_row_header": false,
      "children": [
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "배포 일시"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "2026/03/27 14:00"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "배포 버전"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "1.2.0"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "배포 환경"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "PRODUCT"}, "annotations": {"bold": true, "color": "green"}}]]}},
        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "담당자"}, "annotations": {"bold": true}}], [{"type": "text", "text": {"content": "홍길동"}}]]}}
      ]
    }
  },
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📄 변경 사항"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "금칙어 API v2 연동"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "증분 갱신 로직 추가"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "✅ 배포 절차"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "ECR 이미지 빌드 및 푸시"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "ECS 서비스 업데이트"}}]}},
  {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "헬스체크 확인"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "⚠️ 롤백 계획"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "이전 버전 태그로 ECS 서비스 롤백 후, API 응답 정상 여부 확인"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "✅ 체크리스트"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "to_do", "to_do": {"checked": false, "rich_text": [{"type": "text", "text": {"content": "배포 전 백업 완료"}}]}},
  {"type": "to_do", "to_do": {"checked": false, "rich_text": [{"type": "text", "text": {"content": "배포 스크립트 검증 완료"}}]}},
  {"type": "to_do", "to_do": {"checked": false, "rich_text": [{"type": "text", "text": {"content": "모니터링 설정 확인"}}]}},
  {"type": "to_do", "to_do": {"checked": false, "rich_text": [{"type": "text", "text": {"content": "롤백 절차 확인"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔍 배포 후 확인 사항"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "API 응답 정상 확인"}}]}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "로그 모니터링 (에러율, 지연시간)"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "⚠️ 이슈 및 해결"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "특이사항 없음"}}]}},
  {"type": "paragraph", "paragraph": {"rich_text": []}},
  {
    "type": "heading_1",
    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🔗 참고 자료"}}]}
  },
  {"type": "divider", "divider": {}},
  {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "GitLab MR #123", "link": {"url": "https://gitlab.com/project/-/merge_requests/123"}}}]}}
]
```
