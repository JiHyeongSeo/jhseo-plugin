# 기본 문서 템플릿

범용 기본 문서 템플릿

## 구성

- 개요
- 본문 섹션 (커스텀 제목)
- 참고 자료

## 변수 목록

| 변수명 | 설명 | 예시 |
|--------|------|------|
| overview | 문서 개요 | 이 문서는 시스템 구성을 설명합니다 |
| section_title | 본문 섹션 제목 | 시스템 구성 |
| section_description | 섹션 설명 | 각 컴포넌트의 역할을 정리합니다 |
| item1_name | 항목 1 이름 | API 서버 |
| item1_value | 항목 1 내용 | FastAPI 기반 REST API |
| item2_name | 항목 2 이름 | 데이터베이스 |
| item2_value | 항목 2 내용 | PostgreSQL 15 |
| reference1_url | 참고 자료 1 URL | https://example.com/doc1 |
| reference1_title | 참고 자료 1 제목 | 공식 문서 |
| reference2_url | 참고 자료 2 URL | https://example.com/doc2 |
| reference2_title | 참고 자료 2 제목 | API 레퍼런스 |

## 템플릿 HTML

```xml
<ac:layout>
<ac:layout-section ac:type="single">
<ac:layout-cell>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991106.png" /></ac:image> <strong>개요</strong></h1>
<hr />
<blockquote><p>{overview}</p></blockquote>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/2991/2991112.png" /></ac:image> <strong>{section_title}</strong></h1>
<hr />
<blockquote><p>{section_description}</p></blockquote>

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
<td><p>{item1_name}</p></td>
<td><p>{item1_value}</p></td>
</tr>
<tr>
<td><p>{item2_name}</p></td>
<td><p>{item2_value}</p></td>
</tr>
</tbody>
</table>

<p>&nbsp;</p>

<h1><ac:image ac:height="32"><ri:url ri:value="https://cdn-icons-png.flaticon.com/128/455/455691.png" /></ac:image> <strong>참고 자료</strong></h1>
<hr />
<ul>
<li><p><a href="{reference1_url}">{reference1_title}</a></p></li>
<li><p><a href="{reference2_url}">{reference2_title}</a></p></li>
</ul>

</ac:layout-cell>
</ac:layout-section>
</ac:layout>
```

## 사용 예시

범용적인 문서를 생성할 때 위 변수들을 적절히 채워서 사용합니다. section_title을 통해 본문 섹션의 제목을 커스터마이즈할 수 있습니다.
