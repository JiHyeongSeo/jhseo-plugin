# Confluence REST API Reference

Base URL: `https://confluence.nexon.com`

## 인증

모든 요청에 Bearer 토큰 인증 필요:
```
Authorization: Bearer $CONFLUENCE_API_TOKEN
```

## 엔드포인트

### 1. 페이지 검색

**GET** `/rest/api/content/search`

CQL(Confluence Query Language)을 사용한 검색

**Query Parameters:**
| 파라미터 | 설명 | 예시 |
|----------|------|------|
| cql | CQL 검색 쿼리 | `type=page AND text~"검색어"` |
| expand | 확장할 필드 | `space,ancestors` |
| limit | 최대 결과 수 | `25` |

**CQL 예시:**
```
# 텍스트 검색
type=page AND text~"배포"

# 특정 공간에서 검색
type=page AND space.key="NAD" AND text~"API"

# 제목으로 검색
type=page AND title~"가이드"
```

**curl 예시:**
```bash
curl -s -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  "https://confluence.nexon.com/rest/api/content/search?cql=type=page+AND+text~\"배포\"&expand=space,ancestors&limit=25"
```

### 2. 페이지 조회

**GET** `/rest/api/content/{pageId}`

특정 페이지의 상세 정보 조회

**Path Parameters:**
| 파라미터 | 설명 |
|----------|------|
| pageId | 페이지 ID |

**Query Parameters:**
| 파라미터 | 설명 | 권장값 |
|----------|------|--------|
| expand | 확장할 필드 | `body.storage,ancestors,version,space` |

**curl 예시:**
```bash
curl -s -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  "https://confluence.nexon.com/rest/api/content/2674833208?expand=body.storage,ancestors,version,space"
```

**응답 예시:**
```json
{
  "id": "2674833208",
  "type": "page",
  "title": "유해탐지팀 컨플 문서",
  "space": {"key": "NAD"},
  "version": {"number": 5},
  "body": {
    "storage": {
      "value": "<p>페이지 내용...</p>",
      "representation": "storage"
    }
  }
}
```

### 3. 페이지 생성

**POST** `/rest/api/content`

새 페이지 생성

**Request Body:**
```json
{
  "type": "page",
  "title": "페이지 제목",
  "space": {"key": "NAD"},
  "ancestors": [{"id": "부모페이지ID"}],
  "body": {
    "storage": {
      "value": "<p>페이지 내용</p>",
      "representation": "storage"
    }
  }
}
```

**curl 예시:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://confluence.nexon.com/rest/api/content" \
  -d '{
    "type": "page",
    "title": "(2026/01/29) API 업데이트 배포",
    "space": {"key": "NAD"},
    "ancestors": [{"id": "2674833208"}],
    "body": {
      "storage": {
        "value": "<p>배포 내용...</p>",
        "representation": "storage"
      }
    }
  }'
```

### 4. 페이지 수정

**PUT** `/rest/api/content/{pageId}`

기존 페이지 수정 (버전 번호 증가 필수)

**Request Body:**
```json
{
  "id": "pageId",
  "type": "page",
  "title": "새 제목",
  "space": {"key": "NAD"},
  "body": {
    "storage": {
      "value": "<p>새 내용</p>",
      "representation": "storage"
    }
  },
  "version": {"number": 새버전번호}
}
```

**curl 예시 (버전 조회 후 수정):**
```bash
# 1. 현재 버전 조회
CURRENT_VERSION=$(curl -s -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  "https://confluence.nexon.com/rest/api/content/{pageId}?expand=version" \
  | jq '.version.number')

# 2. 버전 증가하여 수정
NEW_VERSION=$((CURRENT_VERSION + 1))

curl -s -X PUT \
  -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://confluence.nexon.com/rest/api/content/{pageId}" \
  -d "{
    \"id\": \"{pageId}\",
    \"type\": \"page\",
    \"title\": \"업데이트된 제목\",
    \"space\": {\"key\": \"NAD\"},
    \"body\": {
      \"storage\": {
        \"value\": \"<p>업데이트된 내용</p>\",
        \"representation\": \"storage\"
      }
    },
    \"version\": {\"number\": $NEW_VERSION}
  }"
```

### 5. 공간 목록 조회

**GET** `/rest/api/space`

사용 가능한 공간 목록 조회

**Query Parameters:**
| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| limit | 최대 결과 수 | 25 |

**curl 예시:**
```bash
curl -s -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  "https://confluence.nexon.com/rest/api/space?limit=25"
```

### 6. 공간 내 페이지 목록

**GET** `/rest/api/content`

특정 공간의 페이지 목록 조회

**Query Parameters:**
| 파라미터 | 설명 | 예시 |
|----------|------|------|
| spaceKey | 공간 키 | `NAD` |
| limit | 최대 결과 수 | `25` |
| expand | 확장할 필드 | `space,version,ancestors` |

**curl 예시:**
```bash
curl -s -H "Authorization: Bearer $CONFLUENCE_API_TOKEN" \
  "https://confluence.nexon.com/rest/api/content?spaceKey=NAD&limit=25&expand=space,ancestors"
```

## 응답 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 페이지를 찾을 수 없음 |
| 409 | 충돌 (버전 불일치 등) |

## 페이지 URL 형식

페이지 바로가기 URL:
```
https://confluence.nexon.com/pages/viewpage.action?pageId={pageId}
```
