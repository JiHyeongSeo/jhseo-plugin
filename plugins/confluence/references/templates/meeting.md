# 회의록 템플릿

회의 안건, 논의 내용, 결정사항, 후속 조치를 기록하는 템플릿

## 1. 문서 목적

회의에서 논의한 안건, 결정 사항, 후속 조치를 체계적으로 기록합니다. 참석하지 못한 팀원도 회의 내용을 파악할 수 있고, Action Item 추적을 통해 후속 조치가 누락되지 않도록 합니다.

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 회의 정보 | 필수 | 일시, 참석자, 장소/온라인 여부를 테이블로 정리 |
| 2 | 안건 | 필수 | 회의 안건을 번호 목록으로 나열 |
| 3 | 논의 내용 | 필수 | 안건별 h2 소제목 + 논의 내용 기술 |
| 4 | 결정 사항 | 필수 | info 패널 안에 번호 목록으로 정리 |
| 5 | Action Items | 선택 | task-list 매크로로 담당자+기한 포함 |
| 6 | 다음 회의 일정 | 선택 | time 매크로로 다음 회의 일정 표시 |

## 3. 섹션별 작성 가이드

### 회의 정보
- **매크로:** 테이블 (키-값 형태)
- **포함 정보:** 일시, 참석자, 장소(오프라인) 또는 회의 링크(온라인), 회의 목적
- **작성 팁:** 참석자는 이름 나열. 불참자가 있다면 별도 기재

### 안건
- **매크로:** 순서 목록(ol)
- **포함 정보:** 회의에서 다룰 주제 목록
- **작성 팁:** 회의 전 미리 작성하여 공유하면 효율적

### 논의 내용
- **매크로:** h2 소제목 + 일반 텍스트/목록
- **포함 정보:** 안건별 논의 요약, 주요 의견, 쟁점
- **작성 팁:** 안건 번호에 맞춰 h2 소제목으로 구분. 발언자를 명시하면 맥락 파악에 도움

### 결정 사항
- **매크로:** info 패널 + 순서 목록(ol)
- **포함 정보:** 최종 결정 내용, 결정 근거 (필요 시)
- **작성 팁:** 결정된 사항만 명확하게 기록. 미결 사항은 Action Items로 이동

### Action Items (선택)
- **매크로:** task-list 매크로 (ac:task-list)
- **포함 정보:** 할 일, 담당자, 기한
- **작성 팁:** 각 항목에 담당자와 기한을 반드시 포함

### 다음 회의 일정 (선택)
- **매크로:** time 매크로
- **포함 정보:** 다음 회의 일시
- **작성 팁:** 정기 회의라면 주기도 함께 기록

## 4. 자동 삽입 요소

- **제목:** `(YYYY/MM/DD) 회의 주제` 형식
- **요약 (tip 패널):** 문서 최상단에 3줄 이내 회의 요약 (핵심 결정사항 중심)
- **라벨:** `sol-meeting`

## 5. 완성 예시 HTML

```xml




<ac:structured-macro ac:name="tip">
<ac:rich-text-body>
<p>{meeting_purpose}</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>회의 정보</strong></h1>
<hr />

<table>
<colgroup>
<col style="width: 150px;" />
<col style="width: 650px;" />
</colgroup>
<tbody>
<tr>
<td><p><strong>일시</strong></p></td>
<td><p><time datetime="{meeting_date}" /> {meeting_time}</p></td>
</tr>
<tr>
<td><p><strong>장소</strong></p></td>
<td><p>{meeting_location}</p></td>
</tr>
<tr>
<td><p><strong>참석자</strong></p></td>
<td><p>{attendees}</p></td>
</tr>
<tr>
<td><p><strong>불참자</strong></p></td>
<td><p>{absentees}</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991112.png" /></ac:image> <strong>안건</strong></h1>
<hr />

<ol>
<li><p>{agenda1}</p></li>
<li><p>{agenda2}</p></li>
<li><p>{agenda3}</p></li>
</ol>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/1077/1077012.png" /></ac:image> <strong>논의 내용</strong></h1>
<hr />

<h2>{agenda1}</h2>
<p>{discussion1}</p>

<h2>{agenda2}</h2>
<p>{discussion2}</p>

<h2>{agenda3}</h2>
<p>{discussion3}</p>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>결정 사항</strong></h1>
<hr />

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<ol>
<li><p>{decision1}</p></li>
<li><p>{decision2}</p></li>
</ol>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3953/3953226.png" /></ac:image> <strong>Action Items</strong></h1>
<hr />
<blockquote><p>후속 조치가 필요한 항목입니다. 담당자와 기한을 확인하세요.</p></blockquote>

<ac:task-list>
<ac:task>
<ac:task-id>1</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span>{action1} (담당: {action1_assignee}, 기한: {action1_due})</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>2</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span>{action2} (담당: {action2_assignee}, 기한: {action2_due})</span></ac:task-body>
</ac:task>
</ac:task-list>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3686/3686930.png" /></ac:image> <strong>다음 회의 일정</strong></h1>
<hr />
<p><time datetime="{next_meeting_date}" /> {next_meeting_time} - {next_meeting_topic}</p>




```

## 변수 목록

| 변수명 | 설명 | 예시 |
|--------|------|------|
| meeting_purpose | 회의 목적 한 줄 요약 | Q1 스프린트 회고 및 Q2 계획 논의 |
| meeting_date | 회의 일자 (YYYY-MM-DD) | 2026-03-28 |
| meeting_time | 회의 시간 | 14:00~15:00 |
| meeting_location | 장소 또는 온라인 링크 | 회의실 A / Zoom |
| attendees | 참석자 목록 | 김철수, 이영희, 박지민 |
| absentees | 불참자 목록 | 정민수 (휴가) |
| agenda1 | 안건 1 | Q1 스프린트 회고 |
| discussion1 | 안건 1 논의 내용 | 목표 대비 80% 달성. 일정 지연 원인 논의 |
| decision1 | 결정 사항 1 | 스프린트 주기를 2주에서 3주로 변경 |
| action1 | Action Item 1 | 스프린트 보드 설정 변경 |
| action1_assignee | Action Item 1 담당자 | 김철수 |
| action1_due | Action Item 1 기한 | 2026-04-01 |
| next_meeting_date | 다음 회의 일자 | 2026-04-04 |
| next_meeting_time | 다음 회의 시간 | 14:00 |
| next_meeting_topic | 다음 회의 주제 | Q2 첫 번째 스프린트 킥오프 |

## 사용 예시

회의록 생성 시 제목은 `(2026/03/28) Q1 스프린트 회고` 형식으로 작성합니다. 회의 전에 안건을 미리 작성하고, 회의 후 논의 내용/결정 사항/Action Items를 채워 완성합니다.
