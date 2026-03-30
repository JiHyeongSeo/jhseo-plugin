# 배포 문서 템플릿

## 1. 문서 목적

서비스 **배포/패치 기록**을 남길 때 사용한다.
매주 목요일 정기 배포, 긴급 핫픽스 배포 등 모든 배포 이벤트에 대해 하나의 문서를 작성한다.
배포 전 계획, 배포 중 절차, 배포 후 확인까지 전 과정을 문서화하여 추적성을 확보한다.

### 제목 규칙

```
(YYYY/MM/DD) 배포 개요 한 줄 요약
```

- 날짜는 **슬래시** 구분 (예: 2026/03/27)
- 환경명이나 버전 접두어를 제목에 넣지 않음
- 예시: `(2026/03/27) 금칙어 처리 v2 API 기반 증분 갱신`

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 배포 정보 | 필수 | 배포 일시, 버전, 환경, 담당자 등 핵심 메타데이터를 테이블로 정리 |
| 2 | 변경 사항 | 필수 | 이번 배포에 포함된 변경 내역을 목록으로 나열 |
| 3 | 배포 절차 | 필수 | 배포 단계를 순서대로 기술 (ol 또는 ui-steps 매크로) |
| 4 | 롤백 계획 | 필수 | 문제 발생 시 복구 방법을 구체적으로 기술 |
| 5 | 체크리스트 | 필수 | 배포 전/중/후 확인해야 할 항목을 task-list로 구성 |
| 6 | 배포 후 확인 사항 | 필수 | 배포 완료 후 검증해야 할 항목 목록 |
| 7 | 이슈 및 해결 | 필수 | 배포 중 발생한 이슈와 해결 방법. 이슈 없으면 "특이사항 없음" 기재 |
| 8 | 참고 자료 | 선택 | GitLab MR, Jira 티켓, 관련 문서 링크 등 |

## 3. 섹션별 작성 가이드

### 배포 정보

- **매크로/형식:** 테이블 (colgroup으로 열 너비 지정)
- **포함할 항목:** 배포 일시, 배포 버전, 배포 환경, 담당자
- **배포 환경 표기:** status 매크로로 환경을 색상 구분하여 표시
  - **DEV** = Red, **STAGE** = Yellow, **PRODUCT** = Green
- 아이콘: 개요/정보 아이콘 (`2991106.png`)

### 변경 사항

- **형식:** 비순서 목록(ul)
- 각 항목은 "무엇을 변경했는지"를 명확하게 서술
- 관련 Jira 티켓이나 MR 번호가 있으면 함께 기재
- 아이콘: 문서/템플릿 아이콘 (`2991112.png`)

### 배포 절차

- **형식:** 순서 목록(ol) 또는 ui-steps 매크로
- 각 단계는 누가 봐도 따라할 수 있을 만큼 구체적으로 작성
- 명령어가 포함되면 code 매크로 (language=bash, theme=Midnight)로 감싸기
- 아이콘: 체크리스트 아이콘 (`8832108.png`)

### 롤백 계획

- **형식:** 본문 텍스트 또는 순서 목록
- 롤백 트리거 조건, 롤백 절차, 롤백 후 확인 사항을 포함
- 아이콘: 경고/주의 아이콘 (`595067.png`)

### 체크리스트

- **매크로:** ac:task-list
- 배포 전 확인(백업, 스크립트 검증), 배포 중 확인(모니터링), 배포 후 확인(롤백 절차 검토) 항목 구성
- 모든 항목은 초기 상태 `incomplete`로 생성
- 아이콘: 체크리스트 아이콘 (`8832108.png`)

### 배포 후 확인 사항

- **형식:** 비순서 목록(ul)
- API 응답 정상 여부, 로그 모니터링, 성능 지표 등 구체적 확인 항목 나열
- 아이콘: 검색/돋보기 아이콘 (`3686930.png`)

### 이슈 및 해결

- **형식:** 이슈가 있으면 테이블(이슈/원인/해결) 또는 목록, 없으면 "특이사항 없음" 텍스트
- 아이콘: 경고/주의 아이콘 (`595067.png`)

### 참고 자료

- **형식:** ul 안에 a 태그로 링크 목록
- 아이콘: 링크/연결 아이콘 (`455691.png`)

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 라벨 `sol-deployment` | 항상 | 문서 생성 시 자동으로 라벨 부여 |
| ac:layout | 2단 이상 레이아웃 필요 시만 | 단일 컬럼 문서에는 사용하지 않음 (내부 스크롤 방지) |

## 5. 완성 예시 HTML

아래는 축약된 storage format 예시이다. 실제 작성 시 변경 사항, 절차 단계, 체크리스트 항목 수는 내용에 맞게 조정한다.

```xml




<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>배포 정보</strong></h1>
<hr />
<table>
<colgroup>
<col style="width: 200px;" />
<col style="width: 600px;" />
</colgroup>
<tbody>
<tr>
<td><p><strong>배포 일시</strong></p></td>
<td><p>2026/03/27 14:00</p></td>
</tr>
<tr>
<td><p><strong>배포 버전</strong></p></td>
<td><p>1.2.0</p></td>
</tr>
<tr>
<td><p><strong>배포 환경</strong></p></td>
<td>
<p>
<ac:structured-macro ac:name="status">
<ac:parameter ac:name="colour">Green</ac:parameter>
<ac:parameter ac:name="title">PRODUCT</ac:parameter>
</ac:structured-macro>
</p>
</td>
</tr>
<tr>
<td><p><strong>담당자</strong></p></td>
<td><p>홍길동</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991112.png" /></ac:image> <strong>변경 사항</strong></h1>
<hr />
<ul>
<li><p>금칙어 API v2 연동</p></li>
<li><p>증분 갱신 로직 추가</p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>배포 절차</strong></h1>
<hr />
<ol>
<li><p>ECR 이미지 빌드 및 푸시</p></li>
<li><p>ECS 서비스 업데이트</p></li>
<li><p>헬스체크 확인</p></li>
</ol>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/595/595067.png" /></ac:image> <strong>롤백 계획</strong></h1>
<hr />
<p>이전 버전 태그로 ECS 서비스 롤백 후, API 응답 정상 여부 확인</p>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>체크리스트</strong></h1>
<hr />
<ac:task-list>
<ac:task>
<ac:task-id>1</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span>배포 전 백업 완료</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>2</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span>배포 스크립트 검증 완료</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>3</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span>모니터링 설정 확인</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>4</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span>롤백 절차 확인</span></ac:task-body>
</ac:task>
</ac:task-list>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3686/3686930.png" /></ac:image> <strong>배포 후 확인 사항</strong></h1>
<hr />
<ul>
<li><p>API 응답 정상 확인</p></li>
<li><p>로그 모니터링 (에러율, 지연시간)</p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/595/595067.png" /></ac:image> <strong>이슈 및 해결</strong></h1>
<hr />
<p>특이사항 없음</p>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>참고 자료</strong></h1>
<hr />
<ul>
<li><p><a href="https://gitlab.com/project/-/merge_requests/123">GitLab MR #123</a></p></li>
</ul>




```
