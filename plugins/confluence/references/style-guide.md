# Confluence 문서 스타일 가이드

## 1. 문서 레이아웃 구조

### 기본 레이아웃 (ac:layout)
```xml
<ac:layout>
  <ac:layout-section ac:type="single">
    <ac:layout-cell>
      <!-- 콘텐츠 -->
    </ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

### 2단 레이아웃
```xml
<ac:layout>
  <ac:layout-section ac:type="two_equal">
    <ac:layout-cell><!-- 왼쪽 --></ac:layout-cell>
    <ac:layout-cell><!-- 오른쪽 --></ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

## 2. 섹션 헤더 스타일

### 표준 패턴: h1 안에 아이콘(32px) + strong 텍스트 + 수평선
```xml
<h1><ac:image ac:height="32"><ri:url ri:value="https://example.com/icon.png" /></ac:image> <strong>섹션 제목</strong></h1>
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

## 기존 문서 수정 시

기존 Confluence 문서를 수정할 때: 문서의 핵심 내용(텍스트, 정보)은 그대로 유지하고, 스타일(레이아웃, 헤더, 아이콘, 테이블 형식 등)만 이 가이드에 맞게 변경하세요.
