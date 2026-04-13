---
name: drawio-notion
description: draw.io XML을 생성하고 viewer.diagrams.net URL로 인코딩하여 Notion embed 블록으로 삽입
---

# draw.io Notion 다이어그램 스킬

draw.io 다이어그램을 생성하고 Notion 페이지에 embed 블록으로 삽입합니다.
외부 앱 설치 없이 동작합니다 (draw.io Desktop, xvfb 불필요).

## 처리 흐름

1. **draw.io XML 생성** — mxGraphModel 형식으로 직접 작성
2. **viewer URL 인코딩** — Python 스크립트로 viewer.diagrams.net URL 생성
3. **Notion embed 삽입** — Notion MCP로 embed 블록 추가

## draw.io 다이어그램 스타일 가이드

상세 스타일/XML 포맷은 아래 문서를 참고하세요:
- `references/drawio-guide.md`: 다이어그램 유형별 Best Practice (ERD, Flowchart, Sequence, Architecture, BPMN, State, Network), 스텐실/커스텀 아이콘, 공통 레이아웃/엣지 패턴, 파스텔 색상 팔레트

**주의:** 다이어그램 생성 시 반드시 비개발자가 이해하기 쉽도록 고품질 UI/UX 다이어그램 설계 가이드라인을 준수해야 합니다. (아이콘 노드 활용, 직관적 흐름도 번호 부여, 일관된 색상 및 스윔레인 적용)

> **최우선 규칙: 노드와 엣지는 절대 겹치지 않게 배치합니다.**
> - **노드끼리 겹침 금지**: 모든 노드는 충분한 간격을 두고 배치. 노드가 다른 노드 위에 올라가거나 겹치는 것은 절대 불가
> - **엣지가 노드를 관통 금지**: 엣지가 노드의 좌우폭 또는 상하폭을 모두 통과하는지 검사 -> 관통하면 노드 옆으로 waypoint를 추가하여 우회 (상세: `drawio-guide.md` 섹션 9 "엣지-노드 관통 검사")
> - **엣지끼리 겹침 금지**: 여러 엣지가 같은 방향으로 갈 때, 수평 구간의 Y레벨과 수직 구간의 X좌표를 각각 엇갈리게 배치 (최소 20~30px 간격). 배치 후 교차 검증 필수 (상세: `drawio-guide.md` 섹션 9 "여러 엣지를 같은 방향으로 라우팅할 때")
> - **같은 면에서 여러 엣지 연결 시**: 같은 지점에서 뽑지 말고, 면을 따라 균등 간격으로 분산 (`exitX/exitY` 사용)
> - **화살표 라벨 겹침 금지**: 라벨이 다른 노드, 엣지, 라벨과 겹치지 않는 위치에 배치 (`labelBackgroundColor=#ffffff` 필수)
>
> 다이어그램 완성 후 **모든 엣지에 대해 관통 검사**(좌우폭/상하폭 모두 통과 여부)를 수행하고, 겹침이 있으면 waypoint로 우회시키세요.

**아이콘 규칙:**
- 아이콘을 적극적으로 사용할 것. 서버=Python, 메신저=Slack, AWS=해당 프로덕트 아이콘이 기본
- 아이콘이 불확실하면 사용자에게 질문할 것. 외부 URL 아이콘 사용 금지 (내장 스텐실 또는 Base64 SVG만 사용)
- 아이콘 라벨에 `spacingTop=8;` 적용 (8px padding)

## 1단계: draw.io XML 생성 규칙

### 기본 구조 (필수)

```xml
<mxGraphModel adaptiveColors="auto">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- 셀들은 parent="1" -->
  </root>
</mxGraphModel>
```

### 금지 사항
- XML 주석(`<!-- -->`) 절대 사용 금지 — 파싱 오류 발생
- 특수문자 반드시 이스케이프: `&amp;` `&lt;` `&gt;` `&quot;`
- 모든 mxCell은 고유한 id 사용

### 엣지 필수 규칙
모든 edge mxCell은 반드시 자식 요소로 mxGeometry를 가져야 합니다:
```xml
<mxCell id="e1" edge="1" source="A" target="B" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### 기본 스타일 가이드

| 요소 | 권장 스타일 |
|---|---|
| 일반 박스 | `rounded=1;whiteSpace=wrap;html=1;` |
| 강조 박스 | `fillColor=#dae8fc;strokeColor=#6c8ebf;` (파랑) |
| 성공/완료 | `fillColor=#d5e8d4;strokeColor=#82b366;` (초록) |
| 경고/주의 | `fillColor=#fff2cc;strokeColor=#d6b656;` (노랑) |
| 위험/오류 | `fillColor=#f8cecc;strokeColor=#b85450;` (빨강) |
| 데이터베이스 | `shape=cylinder3;` |
| 마름모(분기) | `rhombus;` |

다이어그램 유형별 상세 스타일은 `references/drawio-guide.md`를 참조하세요.

## 2단계: viewer URL 인코딩

다음 Python 코드로 XML을 viewer.diagrams.net URL로 변환합니다:

```python
import zlib, base64, urllib.parse

xml = """<mxGraphModel>...</mxGraphModel>"""

compressed = zlib.compress(xml.encode('utf-8'), level=9)
raw = compressed[2:-4]  # zlib 헤더/체크섬 제거 (raw deflate)
encoded = base64.b64encode(raw).decode('utf-8')
url_encoded = urllib.parse.quote(encoded, safe='')
viewer_url = f'https://viewer.diagrams.net/?tags=%7B%7D&highlight=0&edit=_blank&layers=1&nav=1#R{url_encoded}'

print(viewer_url)
```

이 URL은 외부 서버 없이 XML이 URL에 직접 인코딩됩니다.

## 3단계: Notion embed 블록 삽입

Notion MCP의 `API-patch-block-children`을 사용합니다.

### 삽입할 블록 구조

```json
[
  {
    "type": "heading_2",
    "heading_2": {
      "rich_text": [{"type": "text", "text": {"content": "다이어그램 제목"}}]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "다이어그램 설명"}}]
    }
  },
  {
    "type": "embed",
    "embed": {
      "url": "<viewer_url>"
    }
  }
]
```

### 참고
- embed 블록은 Notion에서 클릭하면 viewer.diagrams.net이 열림
- 인터랙티브 뷰어에서 확대/축소, 편집 가능
- 노션 페이지 ID를 모를 경우 Notion MCP의 `API-post-search`로 검색

## Notion 페이지 구조 참고

- **유해탐지팀 페이지**: `1f2dadb5-6b2f-8069-9d66-c8f27df65215`
- **개인 일정 DB**: `78e9f006-df43-4ccf-9799-a64c930ccedd`

## 사용 예시

```
/drawio-notion 텍스트 탐지 서비스 아키텍처를 유해탐지팀 페이지에 그려줘
/drawio-notion API 호출 시퀀스 다이어그램 만들어서 노션에 올려줘
```

## 주의사항

- Notion MCP가 연결되어 있어야 합니다 (`notionApi` MCP)
- viewer.diagrams.net embed는 Notion에서 iframe으로 렌더링됨
- embed 블록 클릭 시 전체화면 인터랙티브 뷰어로 열림
