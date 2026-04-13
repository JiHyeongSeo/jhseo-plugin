---
name: notion
description: Notion 페이지 검색/조회/생성/수정. "notion", "노션", "문서 생성", "페이지 검색", "배포 노트", "아키텍처", "회의록", "트러블슈팅", "ADR", "라벨" 등의 키워드에서 활성화
---

# Notion 스킬

Notion 페이지를 검색, 조회, 생성, 수정하는 스킬입니다.

## 트리거

다음 키워드가 포함된 요청에서 활성화됩니다:
- "notion", "노션"
- "문서 생성", "페이지 생성", "페이지 만들"
- "페이지 검색", "문서 검색"
- "배포 문서", "배포 노트", "패치 노트"
- "draw.io", "drawio", "다이어그램"
- "아키텍처", "설계 문서", "시스템 구조"
- "회의록", "미팅 노트"
- "트러블슈팅", "장애 기록", "이슈 기록"
- "ADR", "의사결정"

## 환경 설정

**필수:** Notion MCP (`notionApi`)가 연결되어 있어야 합니다.

## 허용 범위

- **페이지:** `1f2dadb5-6b2f-8069-9d66-c8f27df65215` (유해탐지팀 페이지) 및 그 하위 페이지만
- **개인 일정 DB:** `78e9f006-df43-4ccf-9799-a64c930ccedd`

사용자에게 응답할 때:
- 페이지 ID 대신 '유해탐지팀 노션 페이지'라고 표현하세요.

## 서비스·레포 매핑

| 레포지토리 | 서비스명 |
|------------|----------|
| engagement_api_fastapi | 텍스트탐지 API |
| engagement_image_detect_fastapi | 이미지탐지 API |
| clean-chatbot/api | 클린챗봇 백엔드 |
| clean-chatbot/front-new | 클린챗봇 프론트 |
| bws/console-backend, console-front, db-server | 통합 차단어(BWS) |

## 문서 작성 전 확인사항

페이지를 생성하기 전에 반드시 사용자에게 확인:
1. 어떤 페이지 하위에 생성할지 (부모 페이지 위치)
2. 작성할 내용 (제목/개요)

## MCP 도구 사용 방법

Notion MCP(`notionApi`)를 직접 호출하여 동작합니다. 별도 CLI 불필요.

### 페이지 검색
```
MCP 도구: API-post-search
파라미터: query (검색어)
```

### 페이지 조회
```
MCP 도구: API-retrieve-a-page (메타데이터)
MCP 도구: API-get-block-children (본문 블록 내용)
```

### 하위 페이지 트리 조회
```
MCP 도구: API-get-block-children (block_id에 부모 페이지 ID 전달, 재귀 조회)
```

### 페이지 생성
```
MCP 도구: API-post-page
파라미터:
  - parent: { "page_id": "부모페이지ID" }
  - properties: { "title": [{"text": {"content": "페이지 제목"}}] }
  - children: [블록 배열]
```

### 블록 추가 (기존 페이지에)
```
MCP 도구: API-patch-block-children
파라미터:
  - block_id: 페이지 ID
  - children: [추가할 블록 배열]
```

### 페이지 속성 수정
```
MCP 도구: API-patch-page
파라미터: properties (수정할 속성)
```

### 블록 수정
```
MCP 도구: API-update-a-block
파라미터: block_id, 수정할 블록 내용
```

### 블록 삭제
```
MCP 도구: API-delete-a-block
파라미터: block_id
```

### 페이지 이동
```
MCP 도구: API-move-page
```

## 문서 생성 시 자동 삽입 규칙

문서를 생성할 때 다음 규칙을 자동으로 적용합니다:

1. **제목 규칙**: 모든 문서 제목은 `(YYYY/MM/DD) 제목` 형식. 유형별 prefix 추가:
   - 배포 문서 → `(YYYY/MM/DD) [배포] 제목`
   - 가이드 → `(YYYY/MM/DD) [가이드] 제목`
   - 아키텍처 → `(YYYY/MM/DD) [아키텍처] 제목`
   - 트러블슈팅 → `(YYYY/MM/DD) [트러블슈팅] 제목`
   - 회의록 → `(YYYY/MM/DD) [회의록] 제목`
   - ADR → `(YYYY/MM/DD) ADR-{번호}: {요약}`
   - 기본 문서 → `(YYYY/MM/DD) 제목` (prefix 없음)
2. **요약 필수**: 모든 문서 최상단에 callout 블록(💡)으로 3줄 이내 요약 (한 줄 결론 + 핵심 숫자)
3. **TOC 삽입**: 요약 아래에 `table_of_contents` 블록 삽입
4. **작성 원칙**: 40자 이내 문장, 3줄 이내 문단, 숫자/결과 먼저, bullet point 우선, bold 남발 금지

## Notion 블록 구조 가이드

### Confluence → Notion 블록 매핑

| Confluence 요소 | Notion 블록 타입 | 매핑 상세 |
|---|---|---|
| `ac:tip` 패널 (초록) | `callout` | icon: "💡", color: "green_background" |
| `ac:info` 패널 (파랑) | `callout` | icon: "ℹ️", color: "blue_background" |
| `ac:warning` 패널 (노랑) | `callout` | icon: "⚠️", color: "yellow_background" |
| `ac:note` 패널 (보라) | `callout` | icon: "📝", color: "purple_background" |
| `h1` + `<hr/>` | `heading_1` + `divider` | 섹션 구분 패턴 |
| `h2` | `heading_2` | 소제목 |
| `table` | `table` | table_width, has_column_header 설정 |
| `ac:task-list` | `to_do` 블록 (여러 개) | checked: false |
| `ac:code` 매크로 | `code` 블록 | language 속성 지정 |
| `ac:status` 매크로 | bold 텍스트 + color annotation | DEV=red, STAGE=yellow, PROD=green |
| Easy Heading Free | `table_of_contents` 블록 | 문서 상단에 삽입 |
| `blockquote` | `quote` 블록 | 섹션 설명용 |
| `<p>&nbsp;</p>` (간격) | 빈 `paragraph` 블록 | 섹션 시각적 구분 |
| `ol` / `ul` | `numbered_list_item` / `bulleted_list_item` | |
| `ac:expand` 매크로 | `toggle` 블록 | FAQ 등에 활용 |
| 섹션 아이콘 (flaticon) | heading 텍스트에 이모지 prefix | 📋, 🔧, 📊, ⚠️, ✅, 🔍, 🔗 등 |

### 섹션 헤더 패턴

Confluence에서의 `h1 + 아이콘 + hr` 패턴을 Notion에서는 다음과 같이 구현:

```json
[
  {
    "type": "heading_1",
    "heading_1": {
      "rich_text": [{"type": "text", "text": {"content": "📋 섹션 제목"}}]
    }
  },
  {
    "type": "divider",
    "divider": {}
  }
]
```

### 자주 사용하는 이모지 매핑

| 용도 | 이모지 | Confluence 아이콘 대체 |
|------|--------|----------------------|
| 개요/정보 | 📋 | 2991106.png |
| 문서/변경 | 📄 | 2991112.png |
| 설정/톱니 | 🔧 | 3953226.png |
| 설치/다운로드 | 📥 | 4961654.png |
| 사용자/방법 | 👤 | 1077012.png |
| 체크리스트 | ✅ | 8832108.png |
| 경고/주의 | ⚠️ | 595067.png |
| 검색/확인 | 🔍 | 3686930.png |
| 링크/참고 | 🔗 | 455691.png |
| FAQ/질문 | ❓ | 1055687.png |
| 아키텍처 | 🏗️ | 1055687.png |

## 문서 유형별 템플릿

문서 작성 시 `references/templates/` 폴더의 유형별 가이드라인을 참조하세요:

| 유형 | 템플릿 파일 | 용도 |
|------|------------|------|
| 기본 | `templates/default.md` | 범용 문서 |
| 배포 | `templates/deployment.md` | 서비스 배포/패치 기록 |
| 가이드 | `templates/guide.md` | 설치/설정/사용법 안내 |
| 아키텍처 | `templates/architecture.md` | 시스템 구조/설계 문서 |
| 트러블슈팅 | `templates/troubleshooting.md` | 장애/이슈 원인 분석 및 해결 기록 |
| 회의록 | `templates/meeting.md` | 회의 안건/결정/후속 조치 기록 |
| ADR | `templates/adr.md` | 기술 의사결정 기록 |

## draw.io 다이어그램 삽입

Notion에서 draw.io 다이어그램을 삽입할 때는 **drawio-notion 플러그인**을 사용합니다.
`/drawio-notion` 커맨드를 호출하거나, drawio-notion 스킬의 지침을 따르세요.

## 참조 문서

스타일 가이드 및 템플릿은 references/ 폴더를 참고하세요:
- `references/style-guide.md` - Notion 문서 스타일 가이드
- `references/templates/` - 문서 유형별 가이드라인 (7종)
