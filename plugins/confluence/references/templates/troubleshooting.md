# 트러블슈팅 기록 템플릿

장애/이슈 발생 시 원인 분석과 해결 과정을 기록하는 템플릿

## 1. 문서 목적

장애나 이슈가 발생했을 때 증상, 원인 분석 과정, 해결 방법, 예방 조치를 체계적으로 기록합니다. 동일한 이슈가 재발했을 때 빠르게 참고할 수 있는 지식 베이스 역할을 합니다.

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 개요 | 필수 | warning 패널로 증상 요약 |
| 2 | 증상 | 필수 | 현상 상세 설명, 발생 시간/환경 정보를 테이블로 정리 |
| 3 | 원인 분석 | 필수 | 분석 과정, 로그/에러 메시지를 code block으로 포함 |
| 4 | 해결 방법 | 필수 | ui-steps 또는 순서 목록으로 단계별 해결 절차 기술 |
| 5 | 예방 조치 | 필수 | info 패널로 재발 방지 방안 제시 |
| 6 | 타임라인 | 선택 | 자동번호 테이블로 시간/이벤트/조치 기록 |
| 7 | 관련 이슈 | 선택 | JIRA 매크로로 관련 이슈 링크 |
| 8 | 참고 자료 | 선택 | 관련 문서/링크 목록 |

## 3. 섹션별 작성 가이드

### 개요
- **매크로:** warning 패널
- **포함 정보:** 이슈 한 줄 요약, 영향 범위, 심각도
- **작성 팁:** 한 눈에 어떤 이슈인지 파악할 수 있게 간결하게 작성

### 증상
- **매크로:** 테이블 (발생 정보) + 일반 텍스트 (상세 설명)
- **포함 정보:** 발생 일시, 발생 환경(서버/서비스), 영향 범위, 현상 상세 설명
- **작성 팁:** 재현 조건이 있다면 함께 기록

### 원인 분석
- **매크로:** code 매크로 (로그/에러 메시지) + 일반 텍스트 (분석 과정)
- **포함 정보:** 분석 과정, 핵심 로그/에러 메시지, 근본 원인(Root Cause)
- **작성 팁:** 분석 과정을 시간 순서대로 기술. 로그는 code block으로 가독성 확보

### 해결 방법
- **매크로:** ui-steps 매크로 또는 순서 목록(ol)
- **포함 정보:** 단계별 해결 절차, 실행한 명령어/설정 변경 내용
- **작성 팁:** 다른 사람이 그대로 따라할 수 있을 정도로 구체적으로 작성

### 예방 조치
- **매크로:** info 패널
- **포함 정보:** 재발 방지를 위한 모니터링/알림 설정, 코드/설정 개선 사항, 프로세스 변경
- **작성 팁:** 실행 가능한 구체적인 조치를 기록

### 타임라인 (선택)
- **매크로:** 자동번호 테이블 (data-snooker-col-series="numbers")
- **포함 정보:** 시간, 이벤트, 조치
- **작성 팁:** 장애 발생부터 완전 복구까지 시간 순서대로 기록

### 관련 이슈 (선택)
- **매크로:** JIRA 매크로
- **포함 정보:** 관련 JIRA 이슈 키

### 참고 자료 (선택)
- **매크로:** 링크 목록 (ul + a 태그)
- **포함 정보:** 관련 문서, 외부 참고 자료 링크

## 4. 자동 삽입 요소

- **제목:** `(YYYY/MM/DD) 이슈 요약` 형식
- **요약 (warning 패널):** 문서 최상단에 3줄 이내 이슈 요약 (트러블슈팅은 warning 패널 사용)
- **라벨:** `sol-troubleshooting`

## 5. 완성 예시 HTML

```xml




<ac:structured-macro ac:name="warning">
<ac:rich-text-body>
<p><strong>{issue_summary}</strong> - {impact_scope}</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/595/595067.png" /></ac:image> <strong>증상</strong></h1>
<hr />
<blockquote><p>이슈 발생 환경과 현상을 정리합니다.</p></blockquote>

<table>
<colgroup>
<col style="width: 200px;" />
<col style="width: 600px;" />
</colgroup>
<tbody>
<tr>
<td><p><strong>발생 일시</strong></p></td>
<td><p>{occurrence_datetime}</p></td>
</tr>
<tr>
<td><p><strong>발생 환경</strong></p></td>
<td><p>{environment}</p></td>
</tr>
<tr>
<td><p><strong>영향 범위</strong></p></td>
<td><p>{impact_scope}</p></td>
</tr>
<tr>
<td><p><strong>심각도</strong></p></td>
<td><p><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">{severity_color}</ac:parameter><ac:parameter ac:name="title">{severity}</ac:parameter></ac:structured-macro></p></td>
</tr>
</tbody>
</table>

<p><strong>현상 상세:</strong></p>
<p>{symptom_detail}</p>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3686/3686930.png" /></ac:image> <strong>원인 분석</strong></h1>
<hr />
<blockquote><p>이슈의 근본 원인을 분석한 과정과 결과입니다.</p></blockquote>

<p>{analysis_process}</p>

<h3>관련 로그/에러 메시지</h3>
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">text</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[{error_log}]]></ac:plain-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="note">
<ac:rich-text-body>
<p><strong>근본 원인 (Root Cause):</strong> {root_cause}</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>해결 방법</strong></h1>
<hr />
<blockquote><p>이슈를 해결하기 위해 수행한 단계별 절차입니다.</p></blockquote>

<ac:structured-macro ac:name="ui-steps">
<ac:parameter ac:name="size">small</ac:parameter>
<ac:rich-text-body>
<ac:structured-macro ac:name="ui-step">
<ac:rich-text-body>
<p><strong>{step1_title}</strong></p>
<p>{step1_detail}</p>
</ac:rich-text-body>
</ac:structured-macro>
<ac:structured-macro ac:name="ui-step">
<ac:rich-text-body>
<p><strong>{step2_title}</strong></p>
<p>{step2_detail}</p>
</ac:rich-text-body>
</ac:structured-macro>
<ac:structured-macro ac:name="ui-step">
<ac:rich-text-body>
<p><strong>{step3_title}</strong></p>
<p>{step3_detail}</p>
</ac:rich-text-body>
</ac:structured-macro>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>예방 조치</strong></h1>
<hr />

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p><strong>재발 방지를 위한 조치 사항:</strong></p>
<ul>
<li><p>{prevention1}</p></li>
<li><p>{prevention2}</p></li>
<li><p>{prevention3}</p></li>
</ul>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3953/3953226.png" /></ac:image> <strong>타임라인</strong></h1>
<hr />
<blockquote><p>장애 발생부터 복구까지의 시간 순서 기록입니다.</p></blockquote>

<table data-snooker-col-series="numbers" data-snooker-locked-cols="0">
<colgroup>
<col class="numberingColumn" />
<col style="width: 150px;" />
<col style="width: 350px;" />
<col style="width: 300px;" />
</colgroup>
<thead>
<tr>
<th class="numberingColumn" contenteditable="false"><p></p></th>
<th><p><strong>시간</strong></p></th>
<th><p><strong>이벤트</strong></p></th>
<th><p><strong>조치</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td class="numberingColumn" contenteditable="false"><p></p></td>
<td><p>{timeline1_time}</p></td>
<td><p>{timeline1_event}</p></td>
<td><p>{timeline1_action}</p></td>
</tr>
<tr>
<td class="numberingColumn" contenteditable="false"><p></p></td>
<td><p>{timeline2_time}</p></td>
<td><p>{timeline2_event}</p></td>
<td><p>{timeline2_action}</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>관련 이슈</strong></h1>
<hr />
<ul>
<li><p><ac:structured-macro ac:name="jira"><ac:parameter ac:name="key">{jira_key}</ac:parameter></ac:structured-macro></p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/1055/1055687.png" /></ac:image> <strong>참고 자료</strong></h1>
<hr />
<ul>
<li><p><a href="{reference1_url}">{reference1_title}</a></p></li>
</ul>




```

## 변수 목록

| 변수명 | 설명 | 예시 |
|--------|------|------|
| issue_summary | 이슈 한 줄 요약 | API 서버 응답 지연 (5초 이상) |
| impact_scope | 영향 범위 | 전체 사용자 API 호출에 영향 |
| occurrence_datetime | 발생 일시 | 2026-03-28 14:30 KST |
| environment | 발생 환경 | Production - API Server (ap-northeast-2) |
| severity_color | 심각도 Status 색상 | Red |
| severity | 심각도 텍스트 | Critical |
| symptom_detail | 현상 상세 설명 | API 응답 시간이 평균 200ms에서 5초 이상으로 증가 |
| analysis_process | 분석 과정 설명 | CloudWatch 로그 확인 결과 DB 커넥션 풀 고갈 확인 |
| error_log | 에러 로그/메시지 | ERROR: connection pool exhausted |
| root_cause | 근본 원인 | DB 커넥션 풀 max_size 설정이 너무 낮음 |
| step1_title | 해결 1단계 제목 | 긴급 대응 |
| step1_detail | 해결 1단계 내용 | API 서버 재시작으로 임시 복구 |
| prevention1 | 예방 조치 1 | DB 커넥션 풀 사이즈 모니터링 알림 추가 |
| timeline1_time | 타임라인 시간 | 14:30 |
| timeline1_event | 타임라인 이벤트 | 모니터링 알림 발생 |
| timeline1_action | 타임라인 조치 | 담당자 확인 시작 |
| jira_key | JIRA 이슈 키 | PROJECT-456 |
| reference1_url | 참고 자료 URL | https://docs.aws.amazon.com/... |
| reference1_title | 참고 자료 제목 | AWS RDS 커넥션 관리 가이드 |

## 사용 예시

트러블슈팅 문서를 생성할 때 위 변수들을 채워서 사용합니다. 제목은 `(2026/03/28) API 서버 응답 지연 이슈` 형식으로 날짜를 포함해 작성합니다.
