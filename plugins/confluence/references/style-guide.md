# Confluence 문서 스타일 가이드

## 1. 문서 레이아웃 구조

### 기본 레이아웃 (권장: layout 없이 직접 작성)

일반적인 단일 컬럼 문서는 `ac:layout` 없이 콘텐츠를 직접 작성합니다. `ac:layout`을 사용하면 고정 높이 영역이 생겨 **페이지 내부에 불필요한 스크롤**이 발생할 수 있습니다.

```xml
<!-- 권장: layout 없이 바로 콘텐츠 작성 -->
<ac:structured-macro ac:name="tip">
  <ac:rich-text-body><p>문서 개요</p></ac:rich-text-body>
</ac:structured-macro>
<h1>...</h1>
```

### 2단 레이아웃 (필요한 경우에만)

2단 이상 레이아웃이 필요한 경우에만 `ac:layout`을 사용합니다.

```xml
<ac:layout>
  <ac:layout-section ac:type="two_equal">
    <ac:layout-cell><!-- 왼쪽 --></ac:layout-cell>
    <ac:layout-cell><!-- 오른쪽 --></ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

## 2. 섹션 헤더 스타일

### 표준 패턴: h1 안에 아이콘(24px) + strong 텍스트 + 수평선
```xml
<h1><ac:image ac:height="24"><ri:url ri:value="https://example.com/icon.png" /></ac:image> <strong>섹션 제목</strong></h1>
<hr />
```

### 섹션 간 공백
```xml
<p>&nbsp;</p>
```

### 자주 사용되는 아이콘 URL

| 용도 | URL |
|------|-----|
| 개요/정보 | https://cdn-icons-png.flaticon.com/128/2991/2991106.png |
| 설정/톱니 | https://cdn-icons-png.flaticon.com/128/3953/3953226.png |
| 설치/다운로드 | https://cdn-icons-png.flaticon.com/128/4961/4961654.png |
| 사용자/방법 | https://cdn-icons-png.flaticon.com/128/1077/1077012.png |
| 검색/돋보기 | https://cdn-icons-png.flaticon.com/128/3686/3686930.png |
| 문서/템플릿 | https://cdn-icons-png.flaticon.com/128/2991/2991112.png |
| 링크/연결 | https://cdn-icons-png.flaticon.com/128/455/455691.png |
| 라이브러리/책 | https://cdn-icons-png.flaticon.com/128/1055/1055687.png |
| 체크리스트 | https://cdn-icons-png.flaticon.com/128/8832/8832108.png |
| 경고/주의 | https://cdn-icons-png.flaticon.com/128/595/595067.png |

### 첨부파일 아이콘 사용
```xml
<h1><ac:image ac:thumbnail="true" ac:width="32"><ri:attachment ri:filename="icon.png" /></ac:image> <strong>섹션 제목</strong></h1>
<hr />
```
- `ri:url`은 외부 URL 아이콘, `ri:attachment`는 페이지 첨부 이미지 아이콘
- `ac:thumbnail="true"` 속성을 함께 사용하는 것이 일반적

## 3. 섹션 설명 (Blockquote)
```xml
<blockquote>
  <p>이 섹션에서는 시스템 구성 및 연동 현황을 설명합니다.</p>
</blockquote>
```

## 4. 테이블 스타일

### 기본 테이블
```xml
<table>
<colgroup>
<col style="width: 200px;" />
<col style="width: 400px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>항목</strong></p></th>
<th><p><strong>내용</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>항목1</p></td>
<td><p>내용1</p></td>
</tr>
</tbody>
</table>
```

### 테이블 내 Status 매크로 (색상 규칙)

| 색상 | 용도 | 예시 |
|------|------|------|
| Red | 개발/DB 관련 | DEV, DB |
| Yellow | 스테이징/ECR | STAGE, ECR |
| Green | 운영/프로덕션 | PRODUCT, LIVE |
| Blue | S3/기타 인프라 | S3, Lambda |
| Grey | 비활성/미정 | TBD, N/A |

```xml
<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Green</ac:parameter>
  <ac:parameter ac:name="title">PRODUCT</ac:parameter>
</ac:structured-macro>
```

### 자동 번호 매기기 테이블
```xml
<table data-snooker-col-series="numbers" data-snooker-locked-cols="0">
<colgroup>
<col class="numberingColumn" />
<col style="width: 300px;" />
<col style="width: 400px;" />
</colgroup>
<thead>
<tr>
<th class="numberingColumn" contenteditable="false"><p></p></th>
<th><p><strong>항목</strong></p></th>
<th><p><strong>내용</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td class="numberingColumn" contenteditable="false"><p></p></td>
<td><p>항목1</p></td>
<td><p>내용1</p></td>
</tr>
</tbody>
</table>
```
- `data-snooker-col-series="numbers"`: 첫 번째 컬럼에 자동 번호 부여
- `data-snooker-locked-cols="0"`: 번호 컬럼 잠금
- 번호 컬럼의 `<th>`/`<td>`에는 `class="numberingColumn"` + `contenteditable="false"` 속성 사용

## 5. 정보 패널 (Info/Note/Warning/Tip)

### Info 패널 (파란색)
```xml
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>참고 정보를 여기에 작성합니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

### Note 패널 (노란색)
```xml
<ac:structured-macro ac:name="note">
  <ac:rich-text-body>
    <p>주의사항을 여기에 작성합니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

### Warning 패널 (빨간색)
```xml
<ac:structured-macro ac:name="warning">
  <ac:rich-text-body>
    <p>경고 메시지를 여기에 작성합니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

### Tip 패널 (초록색)
```xml
<ac:structured-macro ac:name="tip">
  <ac:rich-text-body>
    <p>성공/팁 메시지를 여기에 작성합니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

## 6. 확장/축소 섹션 (Expand)
```xml
<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">클릭하여 펼치기</ac:parameter>
  <ac:rich-text-body>
    <p>숨겨진 콘텐츠...</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

## 7. 코드 블록

### 권장: code 매크로 + CDATA
```xml
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">python</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[def hello():
    print("Hello, World!")]]></ac:plain-text-body>
</ac:structured-macro>
```

**중요:** CDATA는 단순히 `<![CDATA[...]]>`로 감싸면 됩니다. 복잡한 이스케이프 불필요.

### 대안: pre/code 태그
```xml
<pre><code>def hello():
    print("Hello, World!")</code></pre>
```

### 지원 언어
python, java, javascript, sql, bash, json, yaml, xml, html, css, text

### 테마
Midnight 권장 (어두운 배경)

## 8. 링크 스타일

### 권장: 일반 a 태그 사용
```xml
<p><a href="https://example.com">바로가기</a></p>
```

### 참고: ui-button 매크로 (일부 환경에서 미지원)
```xml
<ac:structured-macro ac:name="ui-button">
  <ac:parameter ac:name="title">바로가기</ac:parameter>
  <ac:parameter ac:name="color">blue</ac:parameter>
  <ac:parameter ac:name="size">medium</ac:parameter>
  <ac:parameter ac:name="newWindow">true</ac:parameter>
  <ac:parameter ac:name="url">https://example.com</ac:parameter>
</ac:structured-macro>
```

색상 옵션: blue, green, red, yellow, grey

## 9. 탭 네비게이션 (Horizontal Nav)
```xml
<ac:structured-macro ac:name="horizontal-nav-group">
  <ac:rich-text-body>
    <ac:structured-macro ac:name="horizontal-nav-item">
      <ac:parameter ac:name="title">탭1</ac:parameter>
      <ac:rich-text-body>
        <p>탭1 콘텐츠</p>
      </ac:rich-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name="horizontal-nav-item">
      <ac:parameter ac:name="title">탭2</ac:parameter>
      <ac:rich-text-body>
        <p>탭2 콘텐츠</p>
      </ac:rich-text-body>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```

## 10. 체크리스트 (Task List)
```xml
<ac:task-list>
  <ac:task>
    <ac:task-id>1</ac:task-id>
    <ac:task-status>incomplete</ac:task-status>
    <ac:task-body><span>할 일 항목 1</span></ac:task-body>
  </ac:task>
  <ac:task>
    <ac:task-id>2</ac:task-id>
    <ac:task-status>complete</ac:task-status>
    <ac:task-body><span>완료된 항목</span></ac:task-body>
  </ac:task>
</ac:task-list>
```

## 11. JIRA 이슈 링크
```xml
<ac:structured-macro ac:name="jira">
  <ac:parameter ac:name="key">PROJECT-123</ac:parameter>
</ac:structured-macro>
```

## 12. 목록 스타일

### 일반 목록
```xml
<ul>
  <li><p>항목 1</p></li>
  <li><p>항목 2</p></li>
</ul>
```

### 순서 목록
```xml
<ol>
  <li><p>첫 번째</p></li>
  <li><p>두 번째</p></li>
</ol>
```

## 13. 단계별 가이드 (ui-steps / ui-step)
```xml
<ac:structured-macro ac:name="ui-steps">
  <ac:parameter ac:name="size">small</ac:parameter>
  <ac:rich-text-body>
    <ac:structured-macro ac:name="ui-step">
      <ac:rich-text-body>
        <p><strong>1단계 제목</strong></p>
        <p>1단계 설명...</p>
      </ac:rich-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name="ui-step">
      <ac:rich-text-body>
        <p><strong>2단계 제목</strong></p>
        <p>2단계 설명...</p>
      </ac:rich-text-body>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```
- `size` 파라미터: `small` 권장
- 각 step 내부에 코드 블록, 이미지, 목록 등 자유롭게 배치 가능
- 설치 가이드, 설정 방법 등 단계별 절차 문서에 적합

## 14. 이모티콘 (ac:emoticon)
```xml
<ac:emoticon ac:name="blue-star" />
<ac:emoticon ac:name="radio button" ac:emoji-id="1f518" />
<ac:emoticon ac:name="light bulb" ac:emoji-id="1f4a1" />
<ac:emoticon ac:name="light-on" />
<ac:emoticon ac:name="tick" />
<ac:emoticon ac:name="cross" />
```

### 자주 사용되는 이모티콘

| 이름 | 용도 |
|------|------|
| blue-star | 단계 제목 강조 |
| radio button | 소제목 마커 |
| light bulb / light-on | 팁/참고 |
| tick / cross | 활성/비활성 표시 |

## 15. 이미지 표시 스타일
```xml
<!-- 기본 이미지 (크기 지정) -->
<ac:image ac:width="800"><ri:attachment ri:filename="screenshot.png" /></ac:image>

<!-- 테두리 + 그림자 효과 -->
<ac:image ac:queryparams="effects=border-simple,shadow-kn" ac:width="800">
  <ri:attachment ri:filename="screenshot.png" />
</ac:image>

<!-- 썸네일 이미지 -->
<ac:image ac:thumbnail="true" ac:height="250">
  <ri:attachment ri:filename="screenshot.png" />
</ac:image>

<!-- 테두리 + 블러 효과 -->
<ac:image ac:queryparams="effects=border-simple,blur-border" ac:width="500">
  <ri:attachment ri:filename="screenshot.png" />
</ac:image>
```

### 자주 사용되는 effects 옵션

| 효과 | 설명 |
|------|------|
| `border-simple,shadow-kn` | 테두리 + 그림자 (가장 많이 사용) |
| `border-simple,blur-border` | 테두리 + 블러 |

### 크기 가이드라인
- 전체 너비 스크린샷: `ac:width="800"`
- 중간 크기: `ac:width="500"` ~ `ac:width="600"`
- 썸네일: `ac:height="250"` 또는 `ac:width="240"`

## 16. 텍스트 색상 스타일
```xml
<!-- 빨간색 주의사항 (가장 많이 사용) -->
<p><em><span style="color: rgb(255,0,0);">※ 주의사항 내용</span></em></p>

<!-- 네이비 색상 설명 텍스트 -->
<span style="color: rgb(0,51,102);">설명 내용</span>
```

### 색상 용도 가이드

| 색상 | RGB | 용도 |
|------|-----|------|
| 빨간색 | rgb(255,0,0) | 주의사항, 경고, 중요 참고 |
| 네이비 | rgb(0,51,102) | 일반 설명 텍스트 강조 |

## 17. 시간/날짜 매크로
```xml
<time datetime="2026-02-19" />
```
- 날짜가 자동 포맷되어 표시됨
- 최초 작성일, 최근 변경일 등에 사용

## 18. 표준 문서 구조

1. **문서 개요 (tip 매크로)** - 페이지 최상단에 tip 패널로 문서 목적 간략히 설명
2. **본문 섹션들** - h1 + 아이콘 + strong 헤더 + hr, 섹션 간 `<p>&nbsp;</p>`로 공백, 테이블 또는 목록으로 정리
3. **참고 자료 / 관련 문서** - 링크 목록

### 문서 개요 tip 매크로 예시
```xml
<ac:structured-macro ac:name="tip">
  <ac:rich-text-body>
    <p>이 문서는 텍스트 탐지 API의 설치 및 설정 방법을 안내합니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

## 19. 모범 사례

1. **일관성:** 동일한 유형의 정보는 동일한 형식으로 표현
2. **시각적 계층:** 아이콘과 구분선으로 섹션 명확히 구분
3. **섹션 간 공백:** `<p>&nbsp;</p>`로 섹션 간 여백 확보
4. **색상 규칙 준수:** Status 매크로 색상은 정해진 규칙대로
5. **테이블 활용:** 비교/목록 정보는 테이블로 정리
6. **확장 매크로:** 부가 정보는 expand로 숨김 처리

## 20. API 사용 시 주의사항

| 기능 | 주의사항 | 해결책 |
|------|----------|--------|
| 코드 블록 | CDATA 이스케이프 복잡하게 하면 안됨 | 단순히 `<![CDATA[...]]>`로 감싸기 |
| ui-button | 일부 환경에서 미지원 | 일반 `<a href>` 사용 |

## 21. 피해야 할 것

- 마크다운 매크로 남용 (네이티브 HTML 선호)
- 과도한 색상 사용
- 불필요한 이미지/아이콘
- 일관성 없는 헤더 스타일
- 테이블 없이 나열식 정보 작성
- 섹션 간 공백 없이 빽빽하게 작성

## 22. draw.io 다이어그램

Confluence에 draw.io 다이어그램을 삽입하려면 **첨부파일 3개 업로드 + 매크로 삽입**이 필요합니다.

### 첨부파일 구조 (3개 필수)

다이어그램 하나당 아래 3개 파일을 페이지에 첨부해야 합니다:

| 파일명 | mediaType | comment | 설명 |
|--------|-----------|---------|------|
| `{diagramName}` | `application/vnd.jgraph.mxfile` | `draw.io diagram` | 메인 다이어그램 XML |
| `{diagramName}.png` | `image/png` | `{diagramName} exported to image` | 미리보기 이미지 (1x1 placeholder PNG 가능) |
| `~{diagramName}.tmp` | `application/xml` | `draw.io Draft` | 드래프트 (메인 XML과 동일 내용) |

**주의:**
- `diagramName`에는 `.drawio` 확장자를 **포함하지 않음** (예: `my-diagram`, NOT `my-diagram.drawio`)
- mediaType이 정확해야 함. 특히 메인 파일은 반드시 `application/vnd.jgraph.mxfile`
- `.png`는 placeholder(1x1 투명 PNG)로도 동작함 — draw.io 플러그인이 첫 조회/편집 시 자동 갱신

### 매크로 형식

```xml
<ac:structured-macro ac:name="drawio">
  <ac:parameter ac:name="border">true</ac:parameter>
  <ac:parameter ac:name="diagramName">{diagramName}</ac:parameter>
  <ac:parameter ac:name="simpleViewer">false</ac:parameter>
  <ac:parameter ac:name="width">{width}</ac:parameter>
  <ac:parameter ac:name="links">auto</ac:parameter>
  <ac:parameter ac:name="tbstyle">top</ac:parameter>
  <ac:parameter ac:name="lbox">true</ac:parameter>
  <ac:parameter ac:name="diagramWidth">{width}</ac:parameter>
  <ac:parameter ac:name="revision">1</ac:parameter>
</ac:structured-macro>
```

- `diagramName`: 첨부파일명과 **정확히 일치** (확장자 없음)
- `width` / `diagramWidth`: 표시 너비 (px). 보통 800~1100
- `revision`: 첨부파일 업데이트 시 증가

### draw.io XML 포맷 (mxGraph)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile>
  <diagram name="Diagram Name" id="unique-id">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1200" pageHeight="800"
                  math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 노드 -->
        <mxCell id="n1" value="텍스트" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="160" height="60" as="geometry"/>
        </mxCell>
        <!-- 엣지 -->
        <mxCell id="e1" style="strokeWidth=2;" edge="1" source="n1" target="n2" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 자주 사용하는 노드 스타일

| 용도 | style |
|------|-------|
| 일반 박스 (파란) | `rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;` |
| 강조 박스 (빨간) | `rounded=1;whiteSpace=wrap;fillColor=#f8cecc;strokeColor=#b85450;strokeWidth=3;` |
| 성공/완료 (초록) | `rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;` |
| 경고/대기 (노랑) | `rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;` |
| 판단/분기 (보라) | `shape=mxgraph.flowchart.decision;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;` |
| 비활성 (회색) | `rounded=1;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#666666;` |
| 시작/끝 (타원) | `shape=ellipse;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;` |
| DB (실린더) | `shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#dae8fc;strokeColor=#6c8ebf;` |

### 전체 작업 순서

1. draw.io XML 작성 (mxGraph 포맷)
2. 페이지에 첨부파일 3개 업로드 (API reference의 "첨부파일 업로드" 참조)
3. 페이지 본문에 drawio 매크로 삽입
4. 페이지 저장/업데이트

## 23. 고품질 UI/UX 다이어그램 설계 가이드라인 (draw.io)

비개발자나 기획자도 쉽게 아키텍처와 흐름을 이해할 수 있도록, draw.io 다이어그램 생성 시 다음 UI/UX 설계 원칙을 준수해야 합니다.

### 가시성 및 시각적 계층 구조 (Visual Hierarchy)
사용자 영역, 내부 시스템, 외부 연동 시스템, 데이터베이스를 명확한 색상 규칙으로 분리하여 인지 부하를 줄입니다.
*   **사용자/클라이언트:** 녹색 계열 (`#d5e8d4`)
*   **핵심 시스템/API:** 파란색 계열 (`#dae8fc`)
*   **외부 서비스/서드파티:** 노란색 계열 (`#fff2cc`)
*   **데이터베이스/저장소:** 보라색 계열 (`#e1d5e7`)

### 비개발자 친화적 표현 (Non-Developer Friendly)
*   **명확한 액션 기반 레이블:** 단순한 API 엔드포인트명(`POST /api/v1/upload`) 대신, 행위 중심의 명확한 문장(`1. 이미지 업로드 요청`)으로 엣지(Edge)를 레이블링합니다.
*   **시간 흐름에 따른 번호 매기기:** 복잡한 흐름은 번호(1, 2, 3...)를 매겨 시계열적 순서를 직관적으로 표현합니다.

### 아이콘 및 시각적 노드 활용
*   단순 사각형(Rectangle) 노드만 나열하는 것을 지양합니다.
*   역할에 맞는 형태를 적극 사용합니다 (예: 사용자는 User 아이콘/Ellipse, DB는 Cylinder 형상 등).
*   **아이콘 스타일 노드 예시:** 텍스트와 함께 시각적 단서를 제공하여 노드의 성격을 바로 파악할 수 있게 구성합니다.

### 그룹핑 및 스윔레인 (Swimlanes / Grouping)
*   시스템 경계(네트워크 경계, VPC, 서비스 도메인 등)는 점선 테두리를 가진 큰 박스로 묶어 구역을 명확히 시각화합니다.
*   **그룹 노드 스타일 예:** `rounded=1;whiteSpace=wrap;fillColor=none;strokeColor=#b85450;strokeWidth=2;dashed=1;`

## 기존 문서 수정 시

기존 Confluence 문서를 수정할 때: 문서의 핵심 내용(텍스트, 정보)은 그대로 유지하고, 스타일(레이아웃, 헤더, 아이콘, 테이블 형식 등)만 이 가이드에 맞게 변경하세요.

## 24. 다이어그램 유형별 Best Practice

**별도 파일로 분리:** `references/drawio-guide.md` 참고

다이어그램 유형별 Shape, 색상, 레이아웃, 예제 XML은 `drawio-guide.md`에서 확인하세요:
- ERD, Flowchart, Sequence, Architecture, BPMN, State, Network/Infra (7종)
- 스텐실 & 커스텀 아이콘 가이드
- 공통 레이아웃 & 엣지 패턴, 파스텔 색상 팔레트

## 25. Easy Heading Free 매크로 (목차/네비게이션)

페이지 내 제목을 기반으로 **오른쪽 사이드바 네비게이션**을 자동 생성합니다. 기본 TOC 매크로와 달리 페이지 본문 영역을 차지하지 않아 스크롤을 아낄 수 있습니다.

```xml
<ac:structured-macro ac:name="easy-heading-free">
  <ac:parameter ac:name="hiddenEditedFlag">true</ac:parameter>
  <ac:parameter ac:name="navigationExpandOption">expand-all-by-default</ac:parameter>
</ac:structured-macro>
```

### 파라미터

| 파라미터 | 값 | 설명 |
|----------|-----|------|
| hiddenEditedFlag | true/false | 편집 플래그 숨김 여부 |
| navigationExpandOption | expand-all-by-default / collapse-all-by-default | 목차 확장/축소 기본값 |

### 삽입 위치

- 문서 최상단, 개요(tip 패널) 바로 아래에 삽입
- Page Properties(details 매크로)가 있는 경우 그 바로 아래에 삽입

> 모든 문서에 항상 삽입합니다.

## 26. Children Display 매크로

현재 페이지의 하위 페이지를 자동으로 목록 표시합니다.

```xml
<ac:structured-macro ac:name="children">
  <ac:parameter ac:name="sort">creation</ac:parameter>
  <ac:parameter ac:name="style">h4</ac:parameter>
  <ac:parameter ac:name="excerptType">simple</ac:parameter>
  <ac:parameter ac:name="first">20</ac:parameter>
  <ac:parameter ac:name="reverse">false</ac:parameter>
  <ac:parameter ac:name="all">true</ac:parameter>
</ac:structured-macro>
```

### 파라미터

| 파라미터 | 값 | 설명 |
|----------|-----|------|
| sort | creation/title/modified | 정렬 기준 |
| style | h2-h6 | 하위 페이지 제목 표시 스타일 |
| excerptType | none/simple/rich | 발췌문 표시 방식 |
| first | 숫자 | 표시할 최대 페이지 수 |
| reverse | true/false | 역순 정렬 |
| all | true/false | 모든 하위 항목(자손 포함) 표시 여부 |

> 허브/인덱스 페이지에서 하위 페이지 자동 목록 표시에 적합합니다.

## 27. Excerpt + Excerpt Include 매크로

한 페이지에서 정의한 콘텐츠를 다른 페이지에서 참조하여 재사용합니다.

### Excerpt (소스 페이지에 작성)
```xml
<ac:structured-macro ac:name="excerpt">
  <ac:parameter ac:name="hidden">true</ac:parameter>
  <ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>
  <ac:rich-text-body>
    <p>재사용할 콘텐츠를 여기에 작성합니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

### Excerpt Include (참조하는 페이지에 작성)
```xml
<ac:structured-macro ac:name="excerpt-include">
  <ac:parameter ac:name="nopanel">true</ac:parameter>
  <ac:rich-text-body>
    <ac:structured-macro ac:name="page">
      <ac:parameter ac:name="">소스 페이지 제목</ac:parameter>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```

> 공통 섹션(팀 소개, 서비스 정보, 연락처)을 한 곳에서 관리하고 여러 문서에서 참조할 때 사용합니다.

## 28. Page Properties + Page Properties Report 매크로

하위 페이지에 구조화된 메타데이터를 정의하고, 부모 페이지에서 집계 테이블로 표시합니다.

### Page Properties (각 하위 페이지에 작성)
```xml
<ac:structured-macro ac:name="details">
  <ac:rich-text-body>
    <table>
    <tbody>
    <tr>
    <th><p>담당자</p></th>
    <td><p>홍길동</p></td>
    </tr>
    <tr>
    <th><p>상태</p></th>
    <td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">운영중</ac:parameter></ac:structured-macro></td>
    </tr>
    <tr>
    <th><p>버전</p></th>
    <td><p>1.2.0</p></td>
    </tr>
    </tbody>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>
```

### Page Properties Report (부모/허브 페이지에 작성)
```xml
<ac:structured-macro ac:name="detailssummary">
  <ac:parameter ac:name="firstcolumn">담당자</ac:parameter>
  <ac:parameter ac:name="headings">담당자,상태,버전</ac:parameter>
  <ac:parameter ac:name="sortBy">담당자</ac:parameter>
  <ac:parameter ac:name="cql">label = "service" and ancestor = currentContent()</ac:parameter>
</ac:structured-macro>
```

### detailssummary 파라미터

| 파라미터 | 값 | 설명 |
|----------|-----|------|
| firstcolumn | 컬럼명 | 첫 번째 컬럼으로 사용할 항목 |
| headings | 쉼표 구분 목록 | 표시할 컬럼 목록 |
| sortBy | 컬럼명 | 정렬 기준 컬럼 |
| cql | CQL 쿼리 | 대상 페이지 필터 조건 |

> 서비스별 메타데이터(버전/담당자/상태)를 구조적으로 관리하고 부모 페이지에서 집계할 때 사용합니다.

## 29. Chart 매크로

테이블 데이터를 기반으로 차트를 생성합니다.

```xml
<ac:structured-macro ac:name="chart">
  <ac:parameter ac:name="type">bar</ac:parameter>
  <ac:parameter ac:name="width">600</ac:parameter>
  <ac:parameter ac:name="height">400</ac:parameter>
  <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
  <ac:rich-text-body>
    <table>
    <thead>
    <tr>
    <th><p></p></th>
    <th><p>1월</p></th>
    <th><p>2월</p></th>
    <th><p>3월</p></th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <th><p>탐지 건수</p></th>
    <td><p>150</p></td>
    <td><p>230</p></td>
    <td><p>180</p></td>
    </tr>
    <tr>
    <th><p>차단 건수</p></th>
    <td><p>120</p></td>
    <td><p>200</p></td>
    <td><p>160</p></td>
    </tr>
    </tbody>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 파라미터

| 파라미터 | 값 | 설명 |
|----------|-----|------|
| type | bar/pie/line/area | 차트 유형 |
| width | 숫자 (px) | 차트 너비 |
| height | 숫자 (px) | 차트 높이 |
| dataOrientation | vertical/horizontal | 데이터 방향 |
| 3D | true/false | 3D 효과 적용 여부 |
| colors | 쉼표 구분 색상값 | 시리즈별 색상 지정 |

> draw.io 없이 테이블 데이터를 간단하게 시각화할 수 있습니다. 매크로 안에 테이블 데이터를 직접 포함하거나, 바로 위 테이블을 참조합니다.

## 30. 문서 작성 원칙 (Readability)

상위 보고 및 팀 간 공유를 고려하여, 모든 문서는 아래 원칙을 따릅니다.

### 30-1. 제목 규칙

모든 문서 제목은 날짜 prefix를 포함합니다:

```
(YYYY/MM/DD) 제목
```

- 날짜는 슬래시 구분 (예: 2026/03/30)
- 날짜와 제목 사이 한 칸 공백
- ADR: `(YYYY/MM/DD) ADR-{번호}: {요약}`

### 30-2. 요약 필수

- 모든 문서 최상단에 tip 패널로 3줄 이내 요약을 작성합니다.
- 한 줄 결론 + 핵심 숫자 형태를 권장합니다.

```xml
<ac:structured-macro ac:name="tip">
  <ac:rich-text-body>
    <p>Redis 캐시 도입으로 API 응답시간 <strong>200ms → 50ms</strong> 개선. 3/28 프로덕션 적용 완료.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 30-3. 문장/문단 길이

- 한 문장은 **40자 이내**
- 한 문단은 **3줄 이내**
- 숫자/결과를 먼저 쓰고, 배경은 뒤에 배치

> **나쁜 예:** 기존 시스템에서 금칙어 사전을 매번 DB에서 조회하는 구조로 인해 평균 응답 시간이 200ms로 느려지는 문제가 발생하여 Redis 캐시를 도입하기로 결정함.
>
> **좋은 예:** 응답시간 200ms → 50ms 개선. 금칙어 사전 DB 조회를 Redis 캐시로 대체.

### 30-4. 시각 비중

- 나열 항목이 3개 이상이면 **테이블** 사용
- 흐름/순서 설명이면 **다이어그램** 또는 순서 목록 사용
- 긴 문단 대신 **bullet point** 우선

### 30-5. 강조 규칙

- 핵심 숫자/결론은 `<strong>` (bold) 처리
- 한 섹션에서 bold는 **1~2개만** — 남발하면 강조 효과가 사라짐
- 결정사항은 tip 패널, 주의사항은 warning 패널 사용
