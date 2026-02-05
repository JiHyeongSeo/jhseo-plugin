# 배포 문서 템플릿

서비스 배포 관련 문서 템플릿 (라이브 배포 기준)

## 제목 형식

```
({deployment_date}) {summary}
```

- **deployment_date:** 2026/01/29 형식 (슬래시)
- **summary:** 환경/버전 접두어 없이 개요만

예시: `(2026/01/29) 금칙어 처리 v2 API 기반 증분 갱신`

## 변수 목록

| 변수명 | 설명 | 예시 |
|--------|------|------|
| deployment_date | 배포 일시 (YYYY/MM/DD) | 2026/01/29 |
| version | 배포 버전 | 1.2.0 |
| summary | 배포 개요 | 금칙어 처리 v2 API 기반 증분 갱신 |
| deployer | 담당자 | 홍길동 |
| changes | 변경 사항 (목록) | 금칙어 API v2 연동, 증분 갱신 로직 추가 |
| step1 | 배포 절차 1단계 | ECR 이미지 빌드 및 푸시 |
| step2 | 배포 절차 2단계 | ECS 서비스 업데이트 |
| step3 | 배포 절차 3단계 | 헬스체크 확인 |
| rollback_plan | 롤백 계획 | 이전 버전 태그로 ECS 롤백 |
| post_deployment_check1 | 배포 후 확인 1 | API 응답 정상 확인 |
| post_deployment_check2 | 배포 후 확인 2 | 로그 모니터링 |
| issues_and_resolutions | 이슈 및 해결 | 특이사항 없음 |
| reference1 | 참고 자료 링크 | GitLab MR 링크 |

## 템플릿 HTML

```xml
<ac:layout>
<ac:layout-section ac:type="single">
<ac:layout-cell>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>배포 정보</strong></h1>
<hr />
<table>
<colgroup>
<col style="width: 200px;" />
<col style="width: 600px;" />
</colgroup>
<tbody>
<tr>
<td><p><strong>배포 일시</strong></p></td>
<td><p>{deployment_date}</p></td>
</tr>
<tr>
<td><p><strong>배포 버전</strong></p></td>
<td><p>{version}</p></td>
</tr>
<tr>
<td><p><strong>담당자</strong></p></td>
<td><p>{deployer}</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991112.png" /></ac:image> <strong>변경 사항</strong></h1>
<hr />
<ul>
<li><p>{changes}</p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>배포 절차</strong></h1>
<hr />
<ol>
<li><p>{step1}</p></li>
<li><p>{step2}</p></li>
<li><p>{step3}</p></li>
</ol>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/595/595067.png" /></ac:image> <strong>롤백 계획</strong></h1>
<hr />
<p>{rollback_plan}</p>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/8832/8832108.png" /></ac:image> <strong>체크리스트</strong></h1>
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

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3686/3686930.png" /></ac:image> <strong>배포 후 확인 사항</strong></h1>
<hr />
<ul>
<li><p>{post_deployment_check1}</p></li>
<li><p>{post_deployment_check2}</p></li>
</ul>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/595/595067.png" /></ac:image> <strong>이슈 및 해결</strong></h1>
<hr />
<p>{issues_and_resolutions}</p>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>참고 자료</strong></h1>
<hr />
<ul>
<li><p>{reference1}</p></li>
</ul>

</ac:layout-cell>
</ac:layout-section>
</ac:layout>
```

## 사용 예시 (curl)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://confluence.nexon.com/rest/api/content" \
  -d '{
    "type": "page",
    "title": "(2026/01/29) 금칙어 처리 v2 API 기반 증분 갱신",
    "space": {"key": "NAD"},
    "ancestors": [{"id": "2674833208"}],
    "body": {
      "storage": {
        "value": "<ac:layout>...(위 템플릿에서 변수 치환)...</ac:layout>",
        "representation": "storage"
      }
    }
  }'
```
