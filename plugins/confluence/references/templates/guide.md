# 가이드 문서 템플릿

## 1. 문서 목적

**설치/설정/사용법 안내** 문서를 작성할 때 사용한다.
API 연동 가이드, 도구 사용법, 환경 설정 매뉴얼, SDK 시작 가이드 등 독자가 단계별로 따라할 수 있는 기술 문서에 적합하다.

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 개요 | 필수 | tip 매크로로 이 가이드가 다루는 내용과 대상 독자를 요약 |
| 2 | 설치 | 필수 | 설치 명령어나 다운로드 방법을 code block으로 제공 |
| 3 | 설정 | 필수 | 환경변수, 설정 파일 등 구성 방법을 code block + info 패널로 안내 |
| 4 | 사용 방법 | 필수 | API 호출, CLI 명령어 등 실제 사용법을 테이블 또는 code block으로 설명 |
| 5 | 참고 자료 | 필수 | 공식 문서, GitLab 저장소 등 관련 링크 |
| 6 | FAQ | 선택 | 자주 묻는 질문을 expand 매크로로 구성 |
| 7 | 트러블슈팅 | 선택 | 흔한 오류와 해결 방법을 warning 패널로 안내 |

## 3. 섹션별 작성 가이드

### 개요

- **매크로:** tip 패널 (초록색)
- **내용:** 이 가이드가 무엇을 설명하는지, 누구를 대상으로 하는지 1~2문장으로 서술
- 사전 요구사항(필요한 권한, 사전 설치 도구 등)이 있으면 함께 언급

### 설치

- **아이콘:** 설치/다운로드 아이콘 (`4961654.png`)
- **형식:** code 매크로 (language=bash, theme=Midnight)
- 패키지 매니저별 설치 명령어, 또는 다운로드 링크 제공
- 여러 환경(OS, 언어 버전)이 있으면 각각 별도 code block으로 구분

### 설정

- **아이콘:** 설정/톱니 아이콘 (`3953226.png`)
- **형식:**
  - blockquote로 설정 개요 설명
  - info 패널로 중요 참고사항(API 키 발급 방법, 권한 요청 절차 등) 안내
  - code 매크로로 설정 파일 예시 제공 (language=json/yaml/env 등, theme=Midnight)
- 필수 설정값과 선택 설정값을 구분하여 서술

### 사용 방법

- **아이콘:** 사용자/방법 아이콘 (`1077012.png`)
- **형식:** 다음 중 내용에 맞는 방식 선택
  - **테이블:** API endpoint 목록처럼 요청-응답 쌍을 정리할 때 (colgroup으로 열 너비 지정)
  - **code block:** 실행 가능한 코드 예시를 보여줄 때
  - **순서 목록:** 단계별 절차를 설명할 때
- blockquote로 사용 방법 개요를 먼저 서술한 뒤 상세 내용 배치

### 참고 자료

- **아이콘:** 링크/연결 아이콘 (`455691.png`)
- **형식:** ul 안에 a 태그로 링크 목록
- 공식 문서, 소스 코드 저장소, 관련 Confluence 문서 등 포함

### FAQ (선택)

- **매크로:** expand (확장/축소)
- 각 질문을 expand의 title로, 답변을 본문으로 구성
- 질문은 독자 관점에서 작성 (예: "API 키는 어디서 발급받나요?")

### 트러블슈팅 (선택)

- **매크로:** warning 패널 (빨간색)
- 흔히 발생하는 오류 메시지와 해결 방법을 쌍으로 기술
- 오류별로 warning 패널을 분리하거나, 하나의 패널 안에 테이블로 정리

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) 가이드 제목` 형식 |
| Easy Heading Free 매크로 | 항상 | 문서 최상단(개요 아래)에 `ac:structured-macro ac:name="easy-heading-free"` 삽입 (`navigationExpandOption=expand-all-by-default`) |
| 요약 (tip 패널) | 항상 | 문서 최상단에 3줄 이내 요약 |
| 라벨 `sol-guide` | 항상 | 문서 생성 시 자동으로 라벨 부여 |
| ac:layout | 2단 이상 레이아웃 필요 시만 | 단일 컬럼 문서에는 사용하지 않음 (내부 스크롤 방지) |

## 5. 완성 예시 HTML

아래는 축약된 storage format 예시이다. 실제 작성 시 설치 명령어, 설정 항목, 사용법 행 수 등은 내용에 맞게 조정한다.

```xml




<ac:structured-macro ac:name="easy-heading-free">
<ac:parameter ac:name="hiddenEditedFlag">true</ac:parameter>
<ac:parameter ac:name="navigationExpandOption">expand-all-by-default</ac:parameter>
</ac:structured-macro>

<ac:structured-macro ac:name="tip">
<ac:rich-text-body>
<p>이 문서는 텍스트탐지 API의 설치 및 설정 방법을 안내합니다.</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>개요</strong></h1>
<hr />
<blockquote><p>텍스트탐지 API를 프로젝트에 연동하기 위한 설치, 설정, 사용 방법을 설명합니다.</p></blockquote>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/4961/4961654.png" /></ac:image> <strong>설치</strong></h1>
<hr />
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">bash</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[pip install engagement-api]]></ac:plain-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/3953/3953226.png" /></ac:image> <strong>설정</strong></h1>
<hr />
<blockquote><p>API 연동을 위해 환경변수를 설정해야 합니다.</p></blockquote>

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p>API 키는 관리자에게 문의하여 발급받으세요.</p>
</ac:rich-text-body>
</ac:structured-macro>

<h3>설정 예시</h3>
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">json</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[{
  "api_key": "your-api-key",
  "base_url": "https://api.example.com/v1",
  "timeout": 30
}]]></ac:plain-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/1077/1077012.png" /></ac:image> <strong>사용 방법</strong></h1>
<hr />
<blockquote><p>다음과 같이 API를 호출합니다.</p></blockquote>

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
<td><p>POST /api/detect</p></td>
<td><p>텍스트 유해성 탐지</p></td>
</tr>
<tr>
<td><p>GET /api/status</p></td>
<td><p>서비스 상태 확인</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>참고 자료</strong></h1>
<hr />
<ul>
<li><p><a href="https://gitlab.com/project/engagement-api">GitLab 저장소</a></p></li>
<li><p><a href="https://api.example.com/docs">API 공식 문서</a></p></li>
</ul>

<p>&nbsp;</p>

<!-- FAQ (선택) -->
<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/1055/1055687.png" /></ac:image> <strong>FAQ</strong></h1>
<hr />
<ac:structured-macro ac:name="expand">
<ac:parameter ac:name="title">API 키는 어디서 발급받나요?</ac:parameter>
<ac:rich-text-body>
<p>팀 관리자에게 Slack으로 요청하면 발급받을 수 있습니다.</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<!-- 트러블슈팅 (선택) -->
<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/595/595067.png" /></ac:image> <strong>트러블슈팅</strong></h1>
<hr />
<ac:structured-macro ac:name="warning">
<ac:rich-text-body>
<p><strong>ConnectionError: Connection refused</strong></p>
<p>VPN 연결 상태를 확인하세요. 사내 네트워크에서만 접근 가능합니다.</p>
</ac:rich-text-body>
</ac:structured-macro>




```
