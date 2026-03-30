# Architecture Decision Record (ADR) 템플릿

기술 의사결정의 배경, 선택지, 최종 결정과 이유를 기록하는 템플릿

## 1. 문서 목적

기술적 의사결정이 필요한 상황에서 배경, 비교한 선택지, 최종 결정과 근거를 체계적으로 기록합니다. "나중에 왜 이렇게 했지?"라는 질문에 답할 수 있는 의사결정 히스토리를 남기는 것이 핵심 목적입니다.

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 메타데이터 | 필수 | Page Properties로 상태/날짜/결정자 메타데이터 관리 |
| 2 | 컨텍스트 | 필수 | 왜 이 결정이 필요했는지 배경 설명 |
| 3 | 선택지 | 필수 | 비교 테이블 + h3 소제목별 bullet point로 각 선택지 상세 설명 |
| 4 | 결정 | 필수 | 최종 선택과 근거, tip 패널로 강조 |
| 5 | 결과 | 필수 | 이 결정으로 인한 영향, 후속 작업 |
| 6 | 관련 ADR | 선택 | 관련된 다른 ADR 링크 목록 |
| 7 | 참고 자료 | 선택 | 외부 참고 자료 링크 |

## 3. 섹션별 작성 가이드

### 메타데이터
- **매크로:** Page Properties (ac:structured-macro ac:name="details") + Status 매크로
- **포함 정보:** 상태(제안됨/승인됨/폐기됨), 작성일, 결정일, 결정자
- **상태 색상 규칙:**
  - 제안됨 (Proposed) = Yellow
  - 승인됨 (Accepted) = Green
  - 폐기됨 (Deprecated) = Grey
  - 대체됨 (Superseded) = Red
- **작성 팁:** ADR의 생명주기를 상태로 관리. 폐기 시 대체 ADR 링크 포함

### 컨텍스트
- **매크로:** 일반 텍스트 + 목록
- **포함 정보:** 현재 상황, 문제점/필요성, 제약 조건, 고려해야 할 요구사항
- **작성 팁:** 기술적 배경 지식이 없는 사람도 이해할 수 있게 작성. "왜" 이 결정이 필요한지에 집중

### 선택지
- **매크로:** 비교 테이블 + h3 소제목 + bullet point (각 선택지 상세)
- **포함 정보:** 옵션명, 장점, 단점, 비고 (비교 테이블) + 각 옵션을 h3 소제목 아래 bullet point로 상세 설명
- **작성 팁:** 최소 2개 이상의 선택지를 비교. "아무것도 안 함"도 유효한 선택지. 내용을 숨기지 않고 바로 보이도록 작성

### 결정
- **매크로:** tip 패널 (최종 결정 강조) + 일반 텍스트 (근거)
- **포함 정보:** 최종 선택한 옵션, 선택 근거, 트레이드오프 인지 사항
- **작성 팁:** 결정의 근거를 명확하게 기술. 어떤 트레이드오프를 감수했는지도 언급

### 결과
- **매크로:** 목록(ul/ol) + note 패널 (주의사항)
- **포함 정보:** 이 결정으로 인해 변경되는 사항, 필요한 후속 작업, 예상되는 리스크
- **작성 팁:** 구체적인 후속 작업과 담당자를 명시하면 실행력이 높아짐

### 관련 ADR (선택)
- **매크로:** 링크 목록 (ul + a 태그)
- **포함 정보:** 이 결정에 영향을 받거나 영향을 준 다른 ADR

### 참고 자료 (선택)
- **매크로:** 링크 목록 (ul + a 태그)
- **포함 정보:** 벤치마크 결과, 기술 블로그, 공식 문서 등 외부 자료

## 4. 자동 삽입 요소

- **라벨:** `sol-adr`
- **Page Properties:** 상태, 작성일, 결정일, 결정자 메타데이터
- **제목 형식:** `(YYYY/MM/DD) ADR-{번호}: {결정 사항 한 줄 요약}`

## 5. 완성 예시 HTML

```xml




<ac:structured-macro ac:name="details">
<ac:rich-text-body>
<table>
<colgroup>
<col style="width: 150px;" />
<col style="width: 650px;" />
</colgroup>
<tbody>
<tr>
<td><p><strong>상태</strong></p></td>
<td><p><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">{status_color}</ac:parameter><ac:parameter ac:name="title">{status}</ac:parameter></ac:structured-macro></p></td>
</tr>
<tr>
<td><p><strong>작성일</strong></p></td>
<td><p><time datetime="{created_date}" /></p></td>
</tr>
<tr>
<td><p><strong>결정일</strong></p></td>
<td><p><time datetime="{decided_date}" /></p></td>
</tr>
<tr>
<td><p><strong>결정자</strong></p></td>
<td><p>{deciders}</p></td>
</tr>
</tbody>
</table>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>컨텍스트</strong></h1>
<hr />
<blockquote><p>이 결정이 필요하게 된 배경과 현재 상황을 설명합니다.</p></blockquote>

<p>{context_description}</p>

<h3>제약 조건</h3>
<ul>
<li><p>{constraint1}</p></li>
<li><p>{constraint2}</p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3686/3686930.png" /></ac:image> <strong>선택지</strong></h1>
<hr />
<blockquote><p>검토한 선택지를 비교합니다.</p></blockquote>

<table>
<colgroup>
<col style="width: 150px;" />
<col style="width: 250px;" />
<col style="width: 250px;" />
<col style="width: 150px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>옵션</strong></p></th>
<th><p><strong>장점</strong></p></th>
<th><p><strong>단점</strong></p></th>
<th><p><strong>비고</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>{option1_name}</p></td>
<td><p>{option1_pros}</p></td>
<td><p>{option1_cons}</p></td>
<td><p>{option1_note}</p></td>
</tr>
<tr>
<td><p>{option2_name}</p></td>
<td><p>{option2_pros}</p></td>
<td><p>{option2_cons}</p></td>
<td><p>{option2_note}</p></td>
</tr>
<tr>
<td><p>{option3_name}</p></td>
<td><p>{option3_pros}</p></td>
<td><p>{option3_cons}</p></td>
<td><p>{option3_note}</p></td>
</tr>
</tbody>
</table>

<h3>옵션 1: {option1_name}</h3>
<ul>
<li><p>{option1_detail_point1}</p></li>
<li><p>{option1_detail_point2}</p></li>
</ul>

<h3>옵션 2: {option2_name}</h3>
<ul>
<li><p>{option2_detail_point1}</p></li>
<li><p>{option2_detail_point2}</p></li>
</ul>

<h3>옵션 3: {option3_name}</h3>
<ul>
<li><p>{option3_detail_point1}</p></li>
<li><p>{option3_detail_point2}</p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>결정</strong></h1>
<hr />

<ac:structured-macro ac:name="tip">
<ac:rich-text-body>
<p><strong>최종 결정: {final_decision}</strong></p>
</ac:rich-text-body>
</ac:structured-macro>

<p><strong>선택 근거:</strong></p>
<p>{decision_rationale}</p>

<p><strong>감수하는 트레이드오프:</strong></p>
<ul>
<li><p>{tradeoff1}</p></li>
<li><p>{tradeoff2}</p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3953/3953226.png" /></ac:image> <strong>결과</strong></h1>
<hr />
<blockquote><p>이 결정으로 인한 영향과 후속 작업을 정리합니다.</p></blockquote>

<p><strong>변경 사항:</strong></p>
<ul>
<li><p>{consequence1}</p></li>
<li><p>{consequence2}</p></li>
</ul>

<p><strong>후속 작업:</strong></p>
<ol>
<li><p>{followup1}</p></li>
<li><p>{followup2}</p></li>
</ol>

<ac:structured-macro ac:name="note">
<ac:rich-text-body>
<p><strong>주의:</strong> {consequence_warning}</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>관련 ADR</strong></h1>
<hr />
<ul>
<li><p><a href="{related_adr1_url}">{related_adr1_title}</a></p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/1055/1055687.png" /></ac:image> <strong>참고 자료</strong></h1>
<hr />
<ul>
<li><p><a href="{reference1_url}">{reference1_title}</a></p></li>
<li><p><a href="{reference2_url}">{reference2_title}</a></p></li>
</ul>




```

## 변수 목록

| 변수명 | 설명 | 예시 |
|--------|------|------|
| status_color | 상태 Status 색상 (Yellow/Green/Grey/Red) | Green |
| status | 상태 텍스트 | 승인됨 |
| created_date | 작성일 (YYYY-MM-DD) | 2026-03-20 |
| decided_date | 결정일 (YYYY-MM-DD) | 2026-03-25 |
| deciders | 결정자 | 김철수, 이영희 |
| context_description | 배경 설명 | 현재 MySQL 5.7을 사용 중이나 EOL 도래로 DB 마이그레이션 필요 |
| constraint1 | 제약 조건 1 | 다운타임 최소화 (30분 이내) |
| option1_name | 옵션 1 이름 | PostgreSQL 16 |
| option1_pros | 옵션 1 장점 | JSON 지원 우수, 확장성 |
| option1_cons | 옵션 1 단점 | 팀 학습 곡선 |
| option1_note | 옵션 1 비고 | 커뮤니티 활발 |
| option1_detail | 옵션 1 상세 설명 | PostgreSQL은 JSON/JSONB 네이티브 지원으로... |
| final_decision | 최종 결정 | PostgreSQL 16으로 마이그레이션 |
| decision_rationale | 결정 근거 | JSON 데이터 처리 요구사항이 높고 장기적 확장성 고려 |
| tradeoff1 | 트레이드오프 1 | 팀원 교육에 2주 소요 예상 |
| consequence1 | 변경 사항 1 | ORM 쿼리 일부 수정 필요 |
| followup1 | 후속 작업 1 | 마이그레이션 스크립트 작성 (담당: 김철수, 기한: 4/10) |
| consequence_warning | 주의사항 | 마이그레이션 기간 동안 읽기 전용 모드 운영 필요 |
| related_adr1_url | 관련 ADR URL | https://confluence.example.com/adr-001 |
| related_adr1_title | 관련 ADR 제목 | ADR-001: ORM 프레임워크 선택 |
| reference1_url | 참고 자료 URL | https://www.postgresql.org/docs/16/ |
| reference1_title | 참고 자료 제목 | PostgreSQL 16 공식 문서 |

## 제목 형식

```
(YYYY/MM/DD) ADR-{번호}: {결정 사항 한 줄 요약}
```

예시: `(2026/03/30) ADR-003: DB를 PostgreSQL 16으로 마이그레이션`

## 사용 예시

ADR 문서를 생성할 때 위 변수들을 채워서 사용합니다. 초기 작성 시 상태는 `Yellow`(제안됨)으로 시작하고, 팀 논의 후 승인되면 `Green`(승인됨)으로 변경합니다. 나중에 해당 결정이 폐기되면 `Grey`(폐기됨)로 변경하고 대체 ADR을 관련 ADR에 링크합니다.
