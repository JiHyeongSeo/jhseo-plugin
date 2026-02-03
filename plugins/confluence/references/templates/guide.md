# 가이드 문서 템플릿

설치/설정/사용법 안내용 가이드 템플릿

## 구성

- 개요
- 설치
- 설정
- 사용 방법
- 참고 자료

## 변수 목록

| 변수명 | 설명 | 예시 |
|--------|------|------|
| overview | 문서 개요 | 텍스트탐지 API 연동 가이드입니다 |
| installation | 설치 명령어 (bash) | pip install engagement-api |
| config_description | 설정 설명 | 환경변수를 설정해야 합니다 |
| config_info | 설정 참고 정보 | API 키는 관리자에게 문의하세요 |
| config_example | 설정 예시 (JSON) | {"api_key": "xxx"} |
| usage_description | 사용 방법 설명 | 다음과 같이 API를 호출합니다 |
| usage1_request | 사용 예시 1 - 요청 | POST /api/detect |
| usage1_action | 사용 예시 1 - 동작 | 텍스트 유해성 탐지 |
| usage2_request | 사용 예시 2 - 요청 | GET /api/status |
| usage2_action | 사용 예시 2 - 동작 | 서비스 상태 확인 |
| reference_url | 참고 자료 URL | https://gitlab.com/... |
| reference_title | 참고 자료 제목 | GitLab 저장소 |

## 템플릿 HTML

```xml
<ac:layout>
<ac:layout-section ac:type="single">
<ac:layout-cell>

<h2><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>개요</strong></h2>
<hr />
<blockquote><p>{overview}</p></blockquote>

<p>&nbsp;</p>

<h2><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/4961/4961654.png" /></ac:image> <strong>설치</strong></h2>
<hr />
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">bash</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[{installation}]]></ac:plain-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h2><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3953/3953226.png" /></ac:image> <strong>설정</strong></h2>
<hr />
<blockquote><p>{config_description}</p></blockquote>

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p>{config_info}</p>
</ac:rich-text-body>
</ac:structured-macro>

<h3>설정 예시</h3>
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">json</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[{config_example}]]></ac:plain-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h2><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/1077/1077012.png" /></ac:image> <strong>사용 방법</strong></h2>
<hr />
<blockquote><p>{usage_description}</p></blockquote>

<table>
<colgroup>
<col style="width: 400px;" />
<col style="width: 400px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>요청</strong></p></th>
<th><p><strong>동작</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>{usage1_request}</p></td>
<td><p>{usage1_action}</p></td>
</tr>
<tr>
<td><p>{usage2_request}</p></td>
<td><p>{usage2_action}</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h2><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>참고 자료</strong></h2>
<hr />
<ul>
<li><p><a href="{reference_url}">{reference_title}</a></p></li>
</ul>

</ac:layout-cell>
</ac:layout-section>
</ac:layout>
```

## 사용 예시

가이드 문서를 생성할 때 위 변수들을 적절히 채워서 API를 호출합니다.
