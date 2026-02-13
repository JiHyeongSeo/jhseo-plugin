---
name: detection-log
description: 텍스트탐지/이미지탐지 API 로그 조회 및 탐지 현황 분석. "텍스트탐지 로그", "이미지탐지 로그", "탐지 로그", "plex 로그", "로그 검색", "로그 조회", "탐지 현황", "호출 통계", "탐지율", "서비스별 통계" 등의 키워드에서 활성화
---

# Detection Log 스킬

Elasticsearch(plex)에서 텍스트탐지/이미지탐지 API 호출 로그를 검색하고 탐지 현황 및 통계를 분석하는 스킬입니다.

## 트리거

다음 키워드가 포함된 요청에서 활성화됩니다:
- "텍스트탐지 로그", "이미지탐지 로그", "텍스트/이미지탐지 로그"
- "탐지 로그", "detection log", "plex 로그", "plex", "ES 로그"
- "로그 검색", "로그 조회", "로그 확인", "로그 보여"
- "탐지 현황", "탐지율", "탐지 통계", "detection rate"
- "호출 통계", "서비스별 통계", "서비스 통계", "호출량"
- "텍스트 검색" (탐지 로그 맥락에서)

## 환경 설정

**필수 환경변수:**
```bash
export ES_USER="engagement-api-http-access-log-api"
export ES_PASSWORD="your-password"
```

## API 사용 방법 (Python CLI)

CLI 경로: `${CLAUDE_PLUGIN_ROOT}/detection_log.py`

**중요:** CLI는 구조화된 옵션만 받습니다. 자연어 문장을 인자로 넘기지 마세요.
- **올바른 사용:** `search -s 430011909 --type badword_kor --detected -n 10`
- **잘못된 사용:** `search "서비스 430011909의 badword_kor 탐지된 로그 10개"`

### 로그 검색 (search)

```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search [옵션]
```

옵션:
- `-f/--from`: 시작 시간 (ISO 8601 또는 ES 상대시간, 기본: `now-1h`)
- `-t/--to`: 종료 시간 (기본: `now`)
- `-s/--service-id`: serviceId 필터
- `--type`: 탐지 타입 필터 (예: `badword_kor`, `ad_global`)
- `--path`: API 경로 필터 (예: `/inference/textclassifier`)
- `-r/--region`: 리전 필터 (`seoul`, `tokyo`, `hongkong`, `oregon`, `singapore`, `frankfurt`)
- `--status`: HTTP 응답 상태 필터 (예: `200`, `500`)
- `-n/--size`: 결과 수 (기본: 20)
- `--sort`: 정렬 (기본: `@timestamp:desc`)
- `--text`: `request.body.data.text`에서 텍스트 검색
- `--detected`: 탐지된 로그만 필터 (`--type` 필수, `stat.{type}.infer_detect > 0` 조건)
- `--undetected`: 미탐 로그만 필터 (`--type` 필수, `stat.{type}.infer_detect == 0` 조건)

예시:
```bash
# 최근 1시간 로그 20건 조회
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search

# 특정 서비스의 최근 3시간 로그
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search -s 40002 -f "now-3h"

# 특정 텍스트가 포함된 로그 검색
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search --text "욕설단어"

# 특정 시간대, 도쿄 리전 로그
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search -f "2026-02-13T00:00:00" -t "2026-02-13T06:00:00" -r tokyo

# badword_kor 타입만 필터
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search --type badword_kor

# 에러 로그만 조회
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search --status 500

# badword_kor로 실제 탐지된 로그만 조회 (infer_detect > 0)
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search --type badword_kor --detected -n 10

# 특정 서비스에서 탐지된 로그만 조회
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search -s 430011909 --type badword_kor --detected -n 10 -f "now-24h"

# badword_kor 미탐(탐지되지 않은) 로그 조회
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search --type badword_kor --undetected -n 10

# 특정 서비스에서 미탐 로그만 조회
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search -s 430011909 --type badword_kor --undetected -n 50 -f "now-24h"
```

### 통계 조회 (stats)

#### 서비스별 통계

```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats service [옵션]
```

serviceId별 호출 수를 내림차순으로 집계합니다.

```bash
# 최근 24시간 서비스별 호출 통계
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats service -f "now-24h"

# 특정 타입에 대한 서비스별 통계
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats service -f "now-24h" --type badword_kor
```

#### 탐지 타입별 통계

```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats type [옵션]
```

각 탐지 타입별 총 호출 수, 탐지 건수, 탐지율(%)을 계산합니다.

```bash
# 최근 24시간 탐지 타입별 통계
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats type -f "now-24h"

# 특정 서비스의 탐지율
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats type -f "now-24h" -s 40002
```

#### 시간대별 추이

```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats timeline [옵션]
```

시간대별 호출 수 히스토그램을 생성합니다.

추가 옵션:
- `--interval`: 시간 간격 (기본: `1h`, 예: `30m`, `1d`)

```bash
# 최근 24시간, 1시간 간격
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats timeline -f "now-24h"

# 최근 7일, 1일 간격
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats timeline -f "now-7d" --interval "1d"

# 특정 서비스 시간별 추이
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats timeline -f "now-24h" -s 40002 --interval "30m"
```

## 주요 필드 요약

| 필드 | 설명 |
|------|------|
| `@timestamp` | 로그 타임스탬프 |
| `request.body.serviceId` | 호출 서비스 식별자 |
| `request.body.types[]` | 사용된 탐지 모델 배열 |
| `request.body.data.text[]` | 입력 텍스트 배열 |
| `request.body.data.len` | 입력 텍스트 수 |
| `request.path` | API 엔드포인트 경로 |
| `response.status` | HTTP 응답 상태 코드 |
| `process_time` | 처리 시간 (ms) |
| `stat.{model}.infer_detect` | 탐지 건수 (0.8 이상인 prediction 수) |
| `stat.{model}.infer_prediction[]` | 모델 예측값 배열 (0~1) |

## 리전 매핑

| 리전 코드 | 리전명 |
|-----------|--------|
| `seoul` | Seoul (기본, 리전 코드 없음) |
| `tokyo` | Tokyo |
| `hongkong` | HongKong |
| `oregon` | Oregon |
| `singapore` | Singapore |
| `frankfurt` | Frankfurt |

## 출력 해석 가이드

- **search 결과**: 각 결과의 `@timestamp`, `serviceId`, `types`, `text`, `process_time`, `status`를 표 형태로 정리. 텍스트가 길면 축약.
- **search --detected 결과**: compact 형식으로 `timestamp`, `service_id`, `detected_texts`(탐지된 텍스트+prediction만) 반환. 전체 stat 객체가 제거되어 출력이 간결함. 바로 테이블로 표시.
- **search --undetected 결과**: compact 형식으로 `timestamp`, `service_id`, `texts`(전체 텍스트+prediction) 반환. 미탐(infer_detect==0) 로그만 포함.
- **stats service**: serviceId별 호출 수를 내림차순 테이블로 표시. 서비스명을 함께 표시하려면 `service-lookup batch`로 한 번에 조회:
  ```bash
  python ${CLAUDE_PLUGIN_ROOT}/../service-lookup/service_lookup.py batch ID1 ID2 ID3 ...
  ```
- **stats type**: 타입별 `total`(총 호출), `detected`(탐지), `rate_percent`(탐지율%)를 테이블로 표시.
- **stats timeline**: 시간 구간별 호출 수를 시간순으로 표시.

## 참조 문서

자세한 필드 및 탐지 타입 정보는 `references/field-reference.md`를 참고하세요.

## 주의사항

- 시간 범위 미지정 시 기본 1시간
- 너무 긴 시간 범위 조회 시 사용자에게 범위 축소 권고
- 텍스트 검색은 ES match 쿼리 사용 (토큰 기반 매칭, 정확 일치가 아님)
- stat 필드의 `#` 포함 타입명(예: `restricted_word#blacklist`)은 ES 필드 경로에서 그대로 사용
