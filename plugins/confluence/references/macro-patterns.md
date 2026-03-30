# Confluence 매크로 조합 패턴북

상황별로 어떤 매크로 조합을 사용해야 하는지 정리한 가이드입니다.
각 패턴에는 상황 설명, 권장 매크로 조합, storage format 예시, 주의사항이 포함되어 있습니다.

---

## 패턴 1: 비교/대조 정보

### 상황
두 가지 이상의 옵션, 환경, 도구 등을 나란히 비교할 때 사용합니다.

### 권장 매크로 조합
- 테이블 (`<table>`) + Status 매크로 (`ac:name="status"`)

### Storage Format 예시
```xml
<table>
<colgroup>
<col style="width: 150px;" />
<col style="width: 250px;" />
<col style="width: 250px;" />
<col style="width: 100px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>항목</strong></p></th>
<th><p><strong>옵션 A</strong></p></th>
<th><p><strong>옵션 B</strong></p></th>
<th><p><strong>권장</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>성능</p></td>
<td><p>초당 1,000건 처리</p></td>
<td><p>초당 5,000건 처리</p></td>
<td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">옵션 B</ac:parameter></ac:structured-macro></td>
</tr>
<tr>
<td><p>비용</p></td>
<td><p>월 100만원</p></td>
<td><p>월 500만원</p></td>
<td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">옵션 A</ac:parameter></ac:structured-macro></td>
</tr>
<tr>
<td><p>도입 난이도</p></td>
<td><p>낮음</p></td>
<td><p>높음</p></td>
<td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Grey</ac:parameter><ac:parameter ac:name="title">동일</ac:parameter></ac:structured-macro></td>
</tr>
</tbody>
</table>
```

### 주의사항
- Status 매크로 색상은 style-guide의 색상 규칙을 준수할 것
- 비교 항목이 5개 이상이면 테이블이 길어지므로 expand 매크로로 감싸는 것을 고려

---

## 패턴 2: 의사결정 기록

### 상황
여러 선택지 중 하나를 결정하고 그 근거를 기록할 때 사용합니다.

### 권장 매크로 조합
- Expand 매크로 (선택지별) + Pros/Cons 테이블 + Status 매크로 (결정 상태)

### Storage Format 예시
```xml
<p><strong>결정 상태:</strong> <ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">결정됨</ac:parameter></ac:structured-macro></p>
<p><strong>최종 결정:</strong> 선택지 A</p>

<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">선택지 A (채택)</ac:parameter>
  <ac:rich-text-body>
    <p>Redis 기반 캐싱 도입</p>
    <table>
    <thead>
    <tr>
    <th><p><strong>장점 (Pros)</strong></p></th>
    <th><p><strong>단점 (Cons)</strong></p></th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td><ul><li><p>응답 속도 90% 개선</p></li><li><p>기존 인프라 활용 가능</p></li></ul></td>
    <td><ul><li><p>캐시 무효화 로직 필요</p></li><li><p>메모리 비용 증가</p></li></ul></td>
    </tr>
    </tbody>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">선택지 B (기각)</ac:parameter>
  <ac:rich-text-body>
    <p>CDN 엣지 캐싱 도입</p>
    <table>
    <thead>
    <tr>
    <th><p><strong>장점 (Pros)</strong></p></th>
    <th><p><strong>단점 (Cons)</strong></p></th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td><ul><li><p>글로벌 성능 개선</p></li></ul></td>
    <td><ul><li><p>도입 비용 높음</p></li><li><p>동적 콘텐츠 캐싱 어려움</p></li></ul></td>
    </tr>
    </tbody>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 주의사항
- 결정 상태 Status를 문서 상단에 명확히 표시할 것 (Green: 결정됨, Yellow: 검토중, Grey: 보류)
- 기각된 선택지도 expand로 남겨두어 이후 참고할 수 있도록 할 것

---

## 패턴 3: 단계별 절차

### 상황
설치, 설정, 배포 등 순서가 있는 작업 절차를 문서화할 때 사용합니다.

### 권장 매크로 조합
- ui-steps 매크로 또는 번호 목록(`<ol>`) + Code 블록 + Info 패널

### Storage Format 예시
```xml
<ac:structured-macro ac:name="ui-steps">
  <ac:parameter ac:name="size">small</ac:parameter>
  <ac:rich-text-body>
    <ac:structured-macro ac:name="ui-step">
      <ac:rich-text-body>
        <p><strong>패키지 설치</strong></p>
        <ac:structured-macro ac:name="code">
        <ac:parameter ac:name="language">bash</ac:parameter>
        <ac:parameter ac:name="theme">Midnight</ac:parameter>
        <ac:plain-text-body><![CDATA[pip install -r requirements.txt]]></ac:plain-text-body>
        </ac:structured-macro>
      </ac:rich-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name="ui-step">
      <ac:rich-text-body>
        <p><strong>환경 변수 설정</strong></p>
        <ac:structured-macro ac:name="code">
        <ac:parameter ac:name="language">bash</ac:parameter>
        <ac:parameter ac:name="theme">Midnight</ac:parameter>
        <ac:plain-text-body><![CDATA[export API_KEY=your-api-key
export DB_HOST=localhost]]></ac:plain-text-body>
        </ac:structured-macro>
        <ac:structured-macro ac:name="info">
          <ac:rich-text-body>
            <p>API_KEY는 관리자에게 문의하세요.</p>
          </ac:rich-text-body>
        </ac:structured-macro>
      </ac:rich-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name="ui-step">
      <ac:rich-text-body>
        <p><strong>서비스 실행</strong></p>
        <ac:structured-macro ac:name="code">
        <ac:parameter ac:name="language">bash</ac:parameter>
        <ac:parameter ac:name="theme">Midnight</ac:parameter>
        <ac:plain-text-body><![CDATA[python main.py --port 8080]]></ac:plain-text-body>
        </ac:structured-macro>
      </ac:rich-text-body>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 주의사항
- ui-steps 매크로가 지원되지 않는 환경에서는 `<ol>` 번호 목록으로 대체
- 각 단계에서 예상되는 결과(성공 메시지 등)를 함께 명시하면 사용자 경험이 향상됨
- 코드 블록 내 민감 정보(API 키, 비밀번호)는 placeholder로 표시

---

## 패턴 4: 주의/위험 사항

### 상황
운영 환경 작업, 데이터 삭제, 비가역적 변경 등 위험한 작업에 대해 경고할 때 사용합니다.

### 권장 매크로 조합
- Warning 패널 (`ac:name="warning"`) + 빨간 텍스트 (`color: rgb(255,0,0)`)

### Storage Format 예시
```xml
<ac:structured-macro ac:name="warning">
  <ac:rich-text-body>
    <p><strong>운영 환경 데이터베이스 작업 시 반드시 백업을 먼저 수행하세요.</strong></p>
    <p>아래 쿼리는 데이터를 영구 삭제하며 복구할 수 없습니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">sql</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[-- 주의: 운영 DB에서 실행 금지
DELETE FROM users WHERE status = 'inactive';]]></ac:plain-text-body>
</ac:structured-macro>

<p><em><span style="color: rgb(255,0,0);">※ 이 작업은 DBA 승인 후에만 실행하세요. 실행 전 반드시 SELECT로 대상 건수를 확인하세요.</span></em></p>
```

### 주의사항
- Warning 패널은 정말 중요한 경고에만 사용하고, 남용하면 경고 효과가 희석됨
- 경고와 함께 안전한 대안이나 사전 확인 절차를 반드시 함께 제시

---

## 패턴 5: 허브/인덱스 페이지

### 상황
팀 위키, 프로젝트 메인 페이지 등 하위 문서를 탐색하기 위한 진입점 페이지를 만들 때 사용합니다.

### 권장 매크로 조합
- Easy Heading Free 매크로 + Children Display 매크로 + Page Properties Report 매크로

### Storage Format 예시
```xml
<ac:structured-macro ac:name="tip">
  <ac:rich-text-body>
    <p>이 페이지는 SOL 팀 서비스 허브입니다. 각 서비스의 상세 정보는 하위 페이지를 참조하세요.</p>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="easy-heading-free">
  <ac:parameter ac:name="hiddenEditedFlag">true</ac:parameter>
  <ac:parameter ac:name="navigationExpandOption">expand-all-by-default</ac:parameter>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><strong>서비스 현황</strong></h1>
<hr />
<ac:structured-macro ac:name="detailssummary">
  <ac:parameter ac:name="firstcolumn">담당자</ac:parameter>
  <ac:parameter ac:name="headings">담당자,상태,버전</ac:parameter>
  <ac:parameter ac:name="sortBy">담당자</ac:parameter>
  <ac:parameter ac:name="cql">label = "service" and ancestor = currentContent()</ac:parameter>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><strong>하위 페이지</strong></h1>
<hr />
<ac:structured-macro ac:name="children">
  <ac:parameter ac:name="sort">title</ac:parameter>
  <ac:parameter ac:name="style">h4</ac:parameter>
  <ac:parameter ac:name="excerptType">simple</ac:parameter>
  <ac:parameter ac:name="all">false</ac:parameter>
</ac:structured-macro>
```

### 주의사항
- Page Properties Report는 하위 페이지에 `details` 매크로가 설정되어 있어야 데이터가 표시됨
- CQL 필터에서 label 조건을 적절히 설정하여 관련 페이지만 집계
- Children Display의 `all` 파라미터를 `true`로 하면 깊은 하위 항목까지 전부 표시되어 목록이 길어질 수 있음

---

## 패턴 6: 데이터 요약/통계

### 상황
월별 실적, 탐지 현황, 처리 건수 등 수치 데이터를 표와 차트로 시각화할 때 사용합니다.

### 권장 매크로 조합
- 테이블 (`<table>`) + Chart 매크로 (`ac:name="chart"`)

### Storage Format 예시
```xml
<h2><strong>월별 처리 현황</strong></h2>

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
    <th><p>요청 건수</p></th>
    <td><p>1200</p></td>
    <td><p>1500</p></td>
    <td><p>1350</p></td>
    </tr>
    <tr>
    <th><p>처리 완료</p></th>
    <td><p>1150</p></td>
    <td><p>1480</p></td>
    <td><p>1300</p></td>
    </tr>
    </tbody>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>위 차트는 매월 1일 기준으로 업데이트됩니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 주의사항
- Chart 매크로 내부의 테이블은 숫자 데이터만 포함해야 함 (Status 매크로 등 비텍스트 요소 사용 금지)
- 데이터 행이 많으면 line 또는 area 차트가 가독성이 좋고, 항목별 비중을 보려면 pie 차트 사용
- 차트와 별도로 원본 테이블도 함께 제공하면 정확한 수치 확인이 가능

---

## 패턴 7: 재사용 콘텐츠

### 상황
팀 소개, 서비스 연락처, 공통 면책 조항 등 여러 문서에서 동일한 내용을 반복 사용할 때 관리합니다.

### 권장 매크로 조합
- Excerpt 매크로 (소스 페이지) + Excerpt Include 매크로 (참조 페이지)

### Storage Format 예시

**소스 페이지 (예: "팀 공통 정보")**
```xml
<ac:structured-macro ac:name="excerpt">
  <ac:parameter ac:name="hidden">true</ac:parameter>
  <ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>
  <ac:rich-text-body>
    <table>
    <tbody>
    <tr>
    <th><p>팀명</p></th>
    <td><p>SOL팀</p></td>
    </tr>
    <tr>
    <th><p>담당자</p></th>
    <td><p>홍길동 (hong@example.com)</p></td>
    </tr>
    <tr>
    <th><p>Slack 채널</p></th>
    <td><p>#sol-team</p></td>
    </tr>
    </tbody>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>
```

**참조 페이지 (예: 각 서비스 문서)**
```xml
<h2><strong>담당 팀 정보</strong></h2>
<ac:structured-macro ac:name="excerpt-include">
  <ac:parameter ac:name="nopanel">true</ac:parameter>
  <ac:rich-text-body>
    <ac:structured-macro ac:name="page">
      <ac:parameter ac:name="">팀 공통 정보</ac:parameter>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 주의사항
- 소스 페이지에 excerpt 매크로가 여러 개 있으면 첫 번째 것만 참조됨
- `hidden` 파라미터를 `true`로 설정하면 소스 페이지에서 해당 영역이 표시되지 않음
- 소스 페이지 제목이 변경되면 참조가 깨지므로 소스 페이지명은 안정적으로 유지할 것

---

## 패턴 8: FAQ/Q&A

### 상황
자주 묻는 질문과 답변을 정리할 때 사용합니다.

### 권장 매크로 조합
- Expand 매크로 (질문을 제목으로, 답변을 본문으로)

### Storage Format 예시
```xml
<h1><strong>자주 묻는 질문 (FAQ)</strong></h1>
<hr />

<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">Q. 비밀번호를 분실했는데 어떻게 재설정하나요?</ac:parameter>
  <ac:rich-text-body>
    <p><strong>A.</strong> 로그인 페이지에서 "비밀번호 찾기"를 클릭하세요.</p>
    <ol>
    <li><p>등록된 이메일 주소를 입력합니다.</p></li>
    <li><p>인증 메일에서 재설정 링크를 클릭합니다.</p></li>
    <li><p>새 비밀번호를 설정합니다.</p></li>
    </ol>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">Q. API 호출 시 429 에러가 발생합니다.</ac:parameter>
  <ac:rich-text-body>
    <p><strong>A.</strong> Rate Limit 초과입니다. 아래 내용을 확인하세요:</p>
    <ac:structured-macro ac:name="info">
      <ac:rich-text-body>
        <p>기본 Rate Limit: 분당 100건. 증가가 필요하면 인프라팀에 요청하세요.</p>
      </ac:rich-text-body>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">Q. 스테이징 환경 접속 방법은?</ac:parameter>
  <ac:rich-text-body>
    <p><strong>A.</strong> VPN 연결 후 아래 주소로 접속하세요:</p>
    <ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">text</ac:parameter>
    <ac:parameter ac:name="theme">Midnight</ac:parameter>
    <ac:plain-text-body><![CDATA[https://staging.example.com]]></ac:plain-text-body>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 주의사항
- 질문 제목은 "Q." 접두사를 붙여 FAQ임을 명확히 할 것
- 답변이 길 경우 expand 내부에 하위 구조(목록, 테이블, 코드 블록)를 활용
- FAQ 항목이 10개 이상이면 카테고리별로 h2 헤더로 분류하는 것을 권장

---

## 패턴 9: 환경별 설정 차이

### 상황
DEV, STAGE, PROD 등 환경별로 다른 설정값이나 접속 정보를 정리할 때 사용합니다.

### 권장 매크로 조합
- Horizontal Nav Group 매크로 (탭으로 환경별 분리)

### Storage Format 예시
```xml
<ac:structured-macro ac:name="horizontal-nav-group">
  <ac:rich-text-body>
    <ac:structured-macro ac:name="horizontal-nav-item">
      <ac:parameter ac:name="title">DEV</ac:parameter>
      <ac:rich-text-body>
        <table>
        <tbody>
        <tr>
        <th><p>API URL</p></th>
        <td><p>https://dev-api.example.com</p></td>
        </tr>
        <tr>
        <th><p>DB Host</p></th>
        <td><p>dev-db.internal:5432</p></td>
        </tr>
        <tr>
        <th><p>Redis</p></th>
        <td><p>dev-redis.internal:6379</p></td>
        </tr>
        </tbody>
        </table>
        <ac:structured-macro ac:name="info">
          <ac:rich-text-body>
            <p>DEV 환경은 VPN 없이 접속 가능합니다.</p>
          </ac:rich-text-body>
        </ac:structured-macro>
      </ac:rich-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name="horizontal-nav-item">
      <ac:parameter ac:name="title">STAGE</ac:parameter>
      <ac:rich-text-body>
        <table>
        <tbody>
        <tr>
        <th><p>API URL</p></th>
        <td><p>https://stage-api.example.com</p></td>
        </tr>
        <tr>
        <th><p>DB Host</p></th>
        <td><p>stage-db.internal:5432</p></td>
        </tr>
        <tr>
        <th><p>Redis</p></th>
        <td><p>stage-redis.internal:6379</p></td>
        </tr>
        </tbody>
        </table>
        <ac:structured-macro ac:name="note">
          <ac:rich-text-body>
            <p>STAGE 환경은 VPN 필수입니다.</p>
          </ac:rich-text-body>
        </ac:structured-macro>
      </ac:rich-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name="horizontal-nav-item">
      <ac:parameter ac:name="title">PROD</ac:parameter>
      <ac:rich-text-body>
        <table>
        <tbody>
        <tr>
        <th><p>API URL</p></th>
        <td><p>https://api.example.com</p></td>
        </tr>
        <tr>
        <th><p>DB Host</p></th>
        <td><p>prod-db.internal:5432</p></td>
        </tr>
        <tr>
        <th><p>Redis</p></th>
        <td><p>prod-redis.internal:6379</p></td>
        </tr>
        </tbody>
        </table>
        <ac:structured-macro ac:name="warning">
          <ac:rich-text-body>
            <p>PROD 환경 직접 접속은 DBA 승인이 필요합니다.</p>
          </ac:rich-text-body>
        </ac:structured-macro>
      </ac:rich-text-body>
    </ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```

### 주의사항
- 각 탭 내부의 테이블 구조(항목)를 동일하게 유지하여 환경 간 비교가 쉽도록 할 것
- PROD 탭에는 warning 패널을 넣어 운영 환경임을 강조
- 비밀번호, 실제 credential 등 민감 정보는 절대 문서에 포함하지 말 것

---

## 패턴 10: 변경 이력

### 상황
문서나 시스템의 변경 이력(Changelog)을 시간순으로 기록할 때 사용합니다.

### 권장 매크로 조합
- 자동번호 테이블 (`data-snooker-col-series="numbers"`) + Time 매크로 (`<time>`) + Status 매크로

### Storage Format 예시
```xml
<h1><strong>변경 이력</strong></h1>
<hr />

<table data-snooker-col-series="numbers" data-snooker-locked-cols="0">
<colgroup>
<col class="numberingColumn" />
<col style="width: 120px;" />
<col style="width: 100px;" />
<col style="width: 300px;" />
<col style="width: 100px;" />
</colgroup>
<thead>
<tr>
<th class="numberingColumn" contenteditable="false"><p></p></th>
<th><p><strong>날짜</strong></p></th>
<th><p><strong>유형</strong></p></th>
<th><p><strong>변경 내용</strong></p></th>
<th><p><strong>담당자</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td class="numberingColumn" contenteditable="false"><p></p></td>
<td><p><time datetime="2026-03-30" /></p></td>
<td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Blue</ac:parameter><ac:parameter ac:name="title">기능추가</ac:parameter></ac:structured-macro></td>
<td><p>Chart 매크로 지원 추가</p></td>
<td><p>홍길동</p></td>
</tr>
<tr>
<td class="numberingColumn" contenteditable="false"><p></p></td>
<td><p><time datetime="2026-03-15" /></p></td>
<td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Red</ac:parameter><ac:parameter ac:name="title">버그수정</ac:parameter></ac:structured-macro></td>
<td><p>API 타임아웃 설정 오류 수정</p></td>
<td><p>김철수</p></td>
</tr>
<tr>
<td class="numberingColumn" contenteditable="false"><p></p></td>
<td><p><time datetime="2026-03-01" /></p></td>
<td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">배포</ac:parameter></ac:structured-macro></td>
<td><p>v1.2.0 운영 배포 완료</p></td>
<td><p>이영희</p></td>
</tr>
</tbody>
</table>
```

### 주의사항
- 최신 항목을 테이블 상단에 배치 (역시간순)
- Status 색상 규칙: Blue(기능추가), Red(버그수정), Green(배포), Yellow(설정변경), Grey(문서수정)
- 변경 이력이 길어지면 분기별로 expand 매크로로 접어서 관리
