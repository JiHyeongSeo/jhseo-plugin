---
name: confluence
description: Confluence 페이지 검색/조회/생성/수정. "confluence", "컨플루언스", "컨플", "문서 생성", "페이지 검색", "배포 노트", "아키텍처", "회의록", "트러블슈팅", "ADR", "라벨" 등의 키워드에서 활성화
---

# Confluence 스킬

Confluence 페이지를 검색, 조회, 생성, 수정하는 스킬입니다.

## 트리거

다음 키워드가 포함된 요청에서 활성화됩니다:
- "confluence", "컨플루언스", "컨플"
- "문서 생성", "페이지 생성", "페이지 만들"
- "페이지 검색", "문서 검색"
- "배포 문서", "배포 노트", "패치 노트"
- "draw.io", "drawio", "다이어그램"
- "아키텍처", "설계 문서", "시스템 구조"
- "회의록", "미팅 노트"
- "트러블슈팅", "장애 기록", "이슈 기록"
- "ADR", "의사결정"
- "라벨", "태그"

## 환경 설정

**필수 환경변수:**
```bash
export CONFLUENCE_API_TOKEN="your-bearer-token"
```

## 허용 범위

- **공간(Space):** NAD (플랫폼 본부 스페이스)
- **페이지:** 2674833208 (유해탐지팀 컨플 문서 최상단) 및 그 하위 페이지만

사용자에게 응답할 때:
- 'NAD' 대신 '플랫폼 본부'
- '2674833208' 대신 '유해탐지팀 컨플 문서'라고 표현하세요.

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
1. 배포할 공간(또는 부모 페이지 위치)
2. 배포할 내용(제목/개요)

## API 사용 방법 (Python CLI)

CLI 경로: `${CLAUDE_PLUGIN_ROOT}/confluence.py`

### 페이지 검색
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py search "검색어"
python ${CLAUDE_PLUGIN_ROOT}/confluence.py search "검색어" -s NAD -l 10
```

### 페이지 조회
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py get {pageId}
```

### 페이지 트리 조회
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py tree
```

### 페이지 생성
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py create -t "제목" -c "<p>내용</p>" -p "부모페이지ID"
```

### 페이지 수정
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py update {pageId} -t "새 제목" -c "<p>새 내용</p>"
```

### 라벨 관리
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py label add {pageId} {labelName}
python ${CLAUDE_PLUGIN_ROOT}/confluence.py label remove {pageId} {labelName}
python ${CLAUDE_PLUGIN_ROOT}/confluence.py label list {pageId}
```

## 문서 생성 시 자동 삽입 규칙

문서를 생성할 때 다음 규칙을 자동으로 적용합니다:

1. **제목 규칙**: 모든 문서 제목은 `(YYYY/MM/DD) 제목` 형식. ADR은 `(YYYY/MM/DD) ADR-{번호}: {요약}`
2. **요약 필수**: 모든 문서 최상단에 tip 패널로 3줄 이내 요약 (한 줄 결론 + 핵심 숫자)
3. **Easy Heading Free 삽입**: 모든 문서에 상단에 Easy Heading Free 매크로 삽입 (오른쪽 사이드바 네비게이션, `navigationExpandOption=expand-all-by-default`)
4. **라벨 자동 부여**: 문서 유형에 따라 `sol-` prefix 라벨을 자동 부여
   - 배포 문서 → `sol-deployment`
   - 가이드 문서 → `sol-guide`
   - 아키텍처 문서 → `sol-architecture`
   - 트러블슈팅 → `sol-troubleshooting`
   - 회의록 → `sol-meeting`
   - ADR → `sol-adr`
5. **허브 페이지**: 하위 페이지를 가진 페이지에는 Children Display 매크로 삽입 고려
6. **작성 원칙**: style-guide.md 섹션 30 준수 (40자 이내 문장, 3줄 이내 문단, 숫자/결과 먼저, bullet point 우선, bold 남발 금지)

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

## 배포 노트 컨벤션

배포/패치 노트 작성 시:
1. **제목 형식:** `(YYYY/MM/DD) 개요`
   - 날짜는 슬래시 형식 (예: 2026/01/29)
   - summary에는 환경([개발] 등), 버전 접두어 넣지 않고 개요만
2. **본문:** deployment 템플릿 사용
   - 템플릿 변수(배포 일시, 버전, 담당자, 변경 사항, 배포 절차 등)를 채워 넣어 템플릿 구조 준수

## draw.io 다이어그램 삽입

Confluence 페이지에 draw.io 다이어그램을 삽입할 때는 **반드시** 아래 절차를 따릅니다.
상세 스타일/XML 포맷은 아래 문서를 참고하세요:
- `references/style-guide.md` 섹션 22-23: draw.io 기본 포맷, Confluence 삽입 방법, UI/UX 설계 가이드라인
- `references/drawio-guide.md`: 다이어그램 유형별 Best Practice (ERD, Flowchart, Sequence, Architecture, BPMN, State, Network), 스텐실/커스텀 아이콘, 공통 레이아웃/엣지 패턴, 파스텔 색상 팔레트

**주의:** 다이어그램 생성 시 반드시 비개발자가 이해하기 쉽도록 고품질 UI/UX 다이어그램 설계 가이드라인을 준수해야 합니다. (아이콘 노드 활용, 직관적 흐름도 번호 부여, 일관된 색상 및 스윔레인 적용)

### 핵심 규칙

1. **첨부파일 3개** 업로드 필수 (다이어그램 하나당):
   - `{diagramName}` — mediaType: `application/vnd.jgraph.mxfile` (메인)
   - `{diagramName}.png` — mediaType: `image/png` (미리보기, placeholder 가능)
   - `~{diagramName}.tmp` — mediaType: `application/xml` (드래프트)
2. **매크로**: `diagramName`은 첨부파일명과 **정확히 일치** (확장자 없음)
3. **매크로 필수 파라미터**: `border`, `diagramName`, `simpleViewer`, `width`, `links`, `tbstyle`, `lbox`, `diagramWidth`, `revision`

### 작업 순서

```
1. draw.io XML(mxGraph 포맷) 작성
2. REST API로 첨부파일 3개 업로드 (api-reference.md "첨부파일 업로드" 참조)
3. 페이지 본문에 drawio 매크로 삽입
4. 페이지 저장/업데이트
```

### 첨부파일 업로드 (Python)

```python
import requests

CONFLUENCE_BASE = "https://confluence.nexon.com"
HEADERS = {"Authorization": f"Bearer {token}", "X-Atlassian-Token": "nocheck"}

def upload(page_id, filename, content_bytes, media_type, comment=""):
    url = f"{CONFLUENCE_BASE}/rest/api/content/{page_id}/child/attachment"
    files = {"file": (filename, content_bytes, media_type)}
    data = {"comment": comment} if comment else {}
    return requests.post(url, headers=HEADERS, files=files, data=data)

# 다이어그램 하나당 3개 업로드
xml_bytes = diagram_xml.encode("utf-8")
upload(page_id, "my-diagram", xml_bytes, "application/vnd.jgraph.mxfile", "draw.io diagram")
upload(page_id, "my-diagram.png", placeholder_png_bytes, "image/png", "my-diagram exported to image")
upload(page_id, "~my-diagram.tmp", xml_bytes, "application/xml", "draw.io Draft")
```

### 매크로 삽입

```xml
<ac:structured-macro ac:name="drawio">
  <ac:parameter ac:name="border">true</ac:parameter>
  <ac:parameter ac:name="diagramName">my-diagram</ac:parameter>
  <ac:parameter ac:name="simpleViewer">false</ac:parameter>
  <ac:parameter ac:name="width">900</ac:parameter>
  <ac:parameter ac:name="links">auto</ac:parameter>
  <ac:parameter ac:name="tbstyle">top</ac:parameter>
  <ac:parameter ac:name="lbox">true</ac:parameter>
  <ac:parameter ac:name="diagramWidth">900</ac:parameter>
  <ac:parameter ac:name="revision">1</ac:parameter>
</ac:structured-macro>
```

## 참조 문서

스타일 가이드 및 템플릿은 references/ 폴더를 참고하세요:
- `references/api-reference.md` - API 엔드포인트 상세 (첨부파일 업로드, 라벨 관리 포함)
- `references/style-guide.md` - Confluence 문서 스타일 가이드 (29개 섹션: 레이아웃, 매크로, draw.io 등)
- `references/drawio-guide.md` - draw.io 다이어그램 유형별 Best Practice (7종)
- `references/macro-patterns.md` - 상황별 매크로 조합 패턴 가이드 (10가지 패턴)
- `references/templates/` - 문서 유형별 가이드라인 (7종)
