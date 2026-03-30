# 아키텍처/설계 문서 템플릿

시스템 구조, 데이터 흐름, 기술 스택을 문서화하는 템플릿

## 1. 문서 목적

새로운 시스템을 구축하거나 기존 시스템의 전체 구조를 문서화할 때 작성합니다. 시스템 아키텍처, 컴포넌트 간 관계, 데이터 흐름, 기술 스택 선택 이유를 한 곳에 정리하여 팀원 간 공유 및 온보딩 자료로 활용합니다.

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 개요 | 필수 | tip 매크로로 문서 목적 간략 설명 |
| 2 | 시스템 아키텍처 | 필수 | draw.io 다이어그램으로 전체 구조 시각화 |
| 3 | 컴포넌트 설명 | 필수 | 각 컴포넌트의 역할, 기술스택, 비고를 테이블로 정리 |
| 4 | 데이터 흐름 | 필수 | 번호 매긴 순서 목록 또는 draw.io 다이어그램 |
| 5 | 기술 스택 | 선택 | 카테고리별 사용 기술, 버전, 용도 테이블 |
| 6 | 의사결정 기록 | 선택 | h3 소제목 + pros/cons 테이블 + tip 패널(결정) |
| 7 | 관련 문서 | 선택 | 참고 링크 목록 |

## 3. 섹션별 작성 가이드

### 개요
- **매크로:** tip 패널
- **포함 정보:** 이 문서가 다루는 시스템 이름, 문서의 목적, 대상 독자
- **작성 팁:** 1~2문장으로 간결하게 작성

### 시스템 아키텍처
- **매크로:** drawio 매크로 (draw.io 다이어그램)
- **포함 정보:** 전체 시스템 구성도, 컴포넌트 간 연결 관계, 외부 연동 시스템
- **작성 팁:** drawio-guide.md의 Architecture 유형 참고. 색상 규칙(사용자=녹색, 핵심시스템=파란색, 외부=노란색, DB=보라색) 준수

### 컴포넌트 설명
- **매크로:** 테이블 (colgroup으로 컬럼 폭 지정)
- **포함 정보:** 컴포넌트명, 역할, 기술스택, 비고
- **작성 팁:** 아키텍처 다이어그램에 표시된 모든 컴포넌트를 빠짐없이 기술

### 데이터 흐름
- **매크로:** 순서 목록(ol) 또는 drawio 매크로
- **포함 정보:** 요청/응답 흐름, 데이터 변환 과정, 비동기 처리 흐름
- **작성 팁:** 번호를 매겨 시간 순서대로 기술. 복잡한 흐름은 draw.io 다이어그램 사용

### 기술 스택 (선택)
- **매크로:** 테이블
- **포함 정보:** 카테고리(Backend/Frontend/Infra 등), 기술명, 버전, 용도
- **작성 팁:** 주요 의존성만 기록. 마이너 라이브러리는 생략

### 의사결정 기록 (선택)
- **매크로:** h3 소제목 + pros/cons 테이블 + tip 패널(결정)
- **포함 정보:** 결정 배경, 비교한 선택지, 최종 결정 및 이유
- **작성 팁:** 각 결정을 h3 소제목으로 구분. 내용을 숨기지 않고 바로 보이도록 작성. 나중에 ADR 문서로 분리할 수도 있음

### 관련 문서 (선택)
- **매크로:** 링크 목록 (ul + a 태그)
- **포함 정보:** 관련 API 문서, 배포 가이드, ADR 등

## 4. 자동 삽입 요소

- **제목:** `(YYYY/MM/DD) 시스템명 아키텍처` 형식
- **Easy Heading Free 매크로:** 문서 최상단(개요 아래)에 사이드바 네비게이션 자동 삽입 (`navigationExpandOption=expand-all-by-default`)
- **요약 (tip 패널):** 문서 최상단에 3줄 이내 요약
- **라벨:** `sol-architecture`

## 5. 완성 예시 HTML

```xml




<ac:structured-macro ac:name="tip">
<ac:rich-text-body>
<p>이 문서는 {system_name} 시스템의 전체 아키텍처와 구성 요소를 설명합니다.</p>
</ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="easy-heading-free">
<ac:parameter ac:name="hiddenEditedFlag">true</ac:parameter>
<ac:parameter ac:name="navigationExpandOption">expand-all-by-default</ac:parameter>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>개요</strong></h1>
<hr />
<blockquote><p>{overview}</p></blockquote>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/1055/1055687.png" /></ac:image> <strong>시스템 아키텍처</strong></h1>
<hr />
<blockquote><p>전체 시스템 구성도입니다. 각 컴포넌트 간 연결 관계와 데이터 흐름을 확인할 수 있습니다.</p></blockquote>

<ac:structured-macro ac:name="drawio">
<ac:parameter ac:name="border">true</ac:parameter>
<ac:parameter ac:name="diagramName">{diagram_name}</ac:parameter>
<ac:parameter ac:name="simpleViewer">false</ac:parameter>
<ac:parameter ac:name="width">1000</ac:parameter>
<ac:parameter ac:name="links">auto</ac:parameter>
<ac:parameter ac:name="tbstyle">top</ac:parameter>
<ac:parameter ac:name="lbox">true</ac:parameter>
<ac:parameter ac:name="diagramWidth">1000</ac:parameter>
<ac:parameter ac:name="revision">1</ac:parameter>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991112.png" /></ac:image> <strong>컴포넌트 설명</strong></h1>
<hr />
<blockquote><p>시스템을 구성하는 각 컴포넌트의 역할과 기술스택을 정리합니다.</p></blockquote>

<table>
<colgroup>
<col style="width: 150px;" />
<col style="width: 300px;" />
<col style="width: 150px;" />
<col style="width: 200px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>컴포넌트명</strong></p></th>
<th><p><strong>역할</strong></p></th>
<th><p><strong>기술스택</strong></p></th>
<th><p><strong>비고</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>{component1_name}</p></td>
<td><p>{component1_role}</p></td>
<td><p>{component1_tech}</p></td>
<td><p>{component1_note}</p></td>
</tr>
<tr>
<td><p>{component2_name}</p></td>
<td><p>{component2_role}</p></td>
<td><p>{component2_tech}</p></td>
<td><p>{component2_note}</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3953/3953226.png" /></ac:image> <strong>데이터 흐름</strong></h1>
<hr />
<blockquote><p>주요 데이터 흐름을 시간 순서대로 설명합니다.</p></blockquote>

<ol>
<li><p>{flow_step1}</p></li>
<li><p>{flow_step2}</p></li>
<li><p>{flow_step3}</p></li>
<li><p>{flow_step4}</p></li>
</ol>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>기술 스택</strong></h1>
<hr />
<blockquote><p>시스템에서 사용하는 주요 기술 스택입니다.</p></blockquote>

<table>
<colgroup>
<col style="width: 150px;" />
<col style="width: 200px;" />
<col style="width: 100px;" />
<col style="width: 350px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>카테고리</strong></p></th>
<th><p><strong>기술</strong></p></th>
<th><p><strong>버전</strong></p></th>
<th><p><strong>용도</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>Backend</p></td>
<td><p>{tech1_name}</p></td>
<td><p>{tech1_version}</p></td>
<td><p>{tech1_purpose}</p></td>
</tr>
<tr>
<td><p>Database</p></td>
<td><p>{tech2_name}</p></td>
<td><p>{tech2_version}</p></td>
<td><p>{tech2_purpose}</p></td>
</tr>
<tr>
<td><p>Infra</p></td>
<td><p>{tech3_name}</p></td>
<td><p>{tech3_version}</p></td>
<td><p>{tech3_purpose}</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3686/3686930.png" /></ac:image> <strong>의사결정 기록</strong></h1>
<hr />
<blockquote><p>주요 기술 의사결정의 배경과 근거를 기록합니다.</p></blockquote>

<h3>{decision1_title}</h3>
<p><strong>배경:</strong> {decision1_context}</p>
<table>
<colgroup>
<col style="width: 200px;" />
<col style="width: 300px;" />
<col style="width: 300px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>선택지</strong></p></th>
<th><p><strong>장점</strong></p></th>
<th><p><strong>단점</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>{decision1_option1}</p></td>
<td><p>{decision1_option1_pros}</p></td>
<td><p>{decision1_option1_cons}</p></td>
</tr>
<tr>
<td><p>{decision1_option2}</p></td>
<td><p>{decision1_option2_pros}</p></td>
<td><p>{decision1_option2_cons}</p></td>
</tr>
</tbody>
</table>
<ac:structured-macro ac:name="tip">
<ac:rich-text-body>
<p><strong>결정:</strong> {decision1_result}</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>관련 문서</strong></h1>
<hr />
<ul>
<li><p><a href="{reference1_url}">{reference1_title}</a></p></li>
<li><p><a href="{reference2_url}">{reference2_title}</a></p></li>
</ul>




```

## 변수 목록

| 변수명 | 설명 | 예시 |
|--------|------|------|
| system_name | 시스템 이름 | 텍스트 탐지 시스템 |
| overview | 문서 개요 | 텍스트 탐지 시스템의 전체 아키텍처를 설명합니다 |
| diagram_name | draw.io 다이어그램 파일명 (확장자 없음) | text-detection-architecture |
| component1_name | 컴포넌트 1 이름 | API Gateway |
| component1_role | 컴포넌트 1 역할 | 외부 요청 수신 및 라우팅 |
| component1_tech | 컴포넌트 1 기술스택 | Kong Gateway |
| component1_note | 컴포넌트 1 비고 | Rate limiting 적용 |
| flow_step1 | 데이터 흐름 1단계 | 클라이언트가 API Gateway에 탐지 요청 전송 |
| tech1_name | 기술 이름 | FastAPI |
| tech1_version | 기술 버전 | 0.104.0 |
| tech1_purpose | 기술 용도 | REST API 서버 |
| decision1_title | 의사결정 제목 | DB 선택: PostgreSQL vs MySQL |
| reference1_url | 참고 자료 URL | https://confluence.example.com/page |
| reference1_title | 참고 자료 제목 | API 설계 문서 |

## 사용 예시

아키텍처 문서를 생성할 때 위 변수들을 채워서 사용합니다. draw.io 다이어그램은 별도로 첨부파일 3개(메인 XML, PNG, tmp)를 업로드해야 합니다. 상세 절차는 style-guide.md의 draw.io 섹션을 참고하세요.
