# 기본 문서 템플릿

## 1. 문서 목적

특정 유형(배포, 가이드 등)에 해당하지 않는 **범용 기본 문서**를 작성할 때 사용한다.
시스템 구성 설명, 현황 정리, 기술 조사 결과, 회의록 등 다양한 용도에 활용할 수 있다.

## 2. 권장 섹션 구성

| 순서 | 섹션명 | 필수/선택 | 설명 |
|------|--------|-----------|------|
| 1 | 개요 | 필수 | tip 매크로로 문서의 목적과 배경을 1~2문장으로 요약 |
| 2 | 본문 섹션 (1개 이상) | 필수 | 문서 주제에 맞는 제목을 자유롭게 설정. h1+아이콘+hr 패턴 사용 |
| 3 | 참고 자료 | 선택 | 관련 문서, 외부 링크 등을 목록으로 정리 |

- 본문 섹션은 문서 내용에 따라 여러 개 추가할 수 있다.
- 섹션 제목은 문서 주제에 맞게 자유롭게 작명한다 (예: "시스템 구성", "연동 현황", "분석 결과").

## 3. 섹션별 작성 가이드

### 개요

- **매크로:** tip 패널 (초록색)
- **내용:** 문서가 다루는 주제와 목적을 간결하게 서술
- 본문을 읽기 전에 전체 맥락을 파악할 수 있어야 함

### 본문 섹션

- **헤더 패턴:** h1 안에 flaticon 아이콘(24px) + strong 텍스트, 바로 아래 hr
- **아이콘 선택:** 섹션 성격에 맞는 아이콘을 style-guide의 아이콘 URL 목록에서 선택
- **섹션 설명:** 필요 시 blockquote로 해당 섹션이 다루는 내용을 한 줄 요약
- **본문 구성:**
  - 비교/목록성 정보는 **테이블** 사용 (colgroup으로 열 너비 지정)
  - 절차/순서가 있는 내용은 **순서 목록**(ol)
  - 나열형 정보는 **비순서 목록**(ul)
  - 코드가 포함되면 **code 매크로** (language 지정, theme=Midnight)
- **섹션 간 공백:** `<p>&nbsp;</p>`로 구분

### 참고 자료

- **아이콘:** 링크/연결 아이콘 사용
- **형식:** ul 안에 a 태그로 링크 목록 구성
- 각 링크는 어떤 문서인지 알 수 있는 제목을 사용

## 4. 자동 삽입 요소

| 요소 | 조건 | 설명 |
|------|------|------|
| 제목 | 항상 | `(YYYY/MM/DD) 제목` 형식 |
| Easy Heading Free 매크로 | 항상 | 문서 최상단(개요 아래)에 `ac:structured-macro ac:name="easy-heading-free"` 삽입 (`navigationExpandOption=expand-all-by-default`) |
| 요약 (tip 패널) | 항상 | 문서 최상단에 3줄 이내 요약 |
| ac:layout | 2단 이상 레이아웃 필요 시만 | 단일 컬럼 문서에는 사용하지 않음 (내부 스크롤 방지) |

## 5. 완성 예시 HTML

아래는 축약된 storage format 예시이다. 실제 작성 시 본문 섹션 수와 테이블 행 수는 내용에 맞게 조정한다.

```xml




<ac:structured-macro ac:name="tip">
<ac:rich-text-body>
<p>이 문서는 OO 시스템의 구성과 연동 현황을 설명합니다.</p>
</ac:rich-text-body>
</ac:structured-macro>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>개요</strong></h1>
<hr />
<blockquote><p>시스템의 전체 구조와 각 컴포넌트의 역할을 정리합니다.</p></blockquote>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991112.png" /></ac:image> <strong>시스템 구성</strong></h1>
<hr />
<blockquote><p>각 컴포넌트의 역할과 기술 스택을 정리합니다.</p></blockquote>

<table>
<colgroup>
<col style="width: 200px;" />
<col style="width: 600px;" />
</colgroup>
<thead>
<tr>
<th><p><strong>항목</strong></p></th>
<th><p><strong>내용</strong></p></th>
</tr>
</thead>
<tbody>
<tr>
<td><p>API 서버</p></td>
<td><p>FastAPI 기반 REST API, ECS Fargate에서 운영</p></td>
</tr>
<tr>
<td><p>데이터베이스</p></td>
<td><p>PostgreSQL 15, RDS Multi-AZ 구성</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="24"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>참고 자료</strong></h1>
<hr />
<ul>
<li><p><a href="https://example.com/architecture">시스템 아키텍처 문서</a></p></li>
<li><p><a href="https://example.com/api-spec">API 스펙 문서</a></p></li>
</ul>




```
