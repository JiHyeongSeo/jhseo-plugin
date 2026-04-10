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

### 스타일 가이드

| 요소 | 권장 스타일 |
|---|---|
| 일반 박스 | `rounded=1;whiteSpace=wrap;html=1;` |
| 강조 박스 | `fillColor=#dae8fc;strokeColor=#6c8ebf;` (파랑) |
| 성공/완료 | `fillColor=#d5e8d4;strokeColor=#82b366;` (초록) |
| 경고/주의 | `fillColor=#fff2cc;strokeColor=#d6b656;` (노랑) |
| 위험/오류 | `fillColor=#f8cecc;strokeColor=#b85450;` (빨강) |
| 데이터베이스 | `shape=cylinder3;` |
| 마름모(분기) | `rhombus;` |

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
