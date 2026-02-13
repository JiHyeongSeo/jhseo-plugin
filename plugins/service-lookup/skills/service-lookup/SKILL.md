---
name: service-lookup
description: 서비스 ID 조회. "서비스 ID", "service id", "서비스 검색", "게임 서비스", "서비스 조회" 등의 키워드에서 활성화
---

# Service Lookup 스킬

게임명이나 메모로 서비스 ID를 검색하는 스킬입니다.

## 트리거

다음 키워드가 포함된 요청에서 활성화됩니다:
- "서비스 ID", "서비스 아이디", "service id", "serviceId"
- "서비스 검색", "서비스 조회", "서비스 찾"
- "게임 서비스", "게임 ID"

## 환경 설정

**필수 환경변수:**
```bash
export NXLOG_SERVICE_USER="your-nxlog-user"
export NXLOG_SERVICE_PASSWORD="your-nxlog-password"
export INFERENCE_API_KEY="your-inference-api-key"
```

## 데이터 소스

### NXLOG 서비스 (source: nxlog)
- 회사 전체 게임에 대해 발급되는 NXLOG 서비스 ID
- 게임명(gameName), 국가(countryName) 기준으로 검색
- `liveGameId`가 서비스 ID

### BWS/탐지 API 서비스 (source: bws)
- BWS(금칙어) 시스템을 사용하는 서비스 ID
- 텍스트탐지 API에 NXLOG 서비스 ID를 발급받지 못할 때 임의 발급된 ID 포함
- memo(서비스 설명) 기준으로 검색
- type 필드: "NXLOG 서비스ID" 또는 "임의 발급"

## API 사용 방법 (Python CLI)

CLI 경로: `${CLAUDE_PLUGIN_ROOT}/service_lookup.py`

### 서비스 검색

```bash
python ${CLAUDE_PLUGIN_ROOT}/service_lookup.py search "검색어" [--source all|nxlog|bws]
```

옵션:
- `검색어`: 게임명, 메모, 서비스 ID 중 일부 (대소문자 무관)
- `--source`: 조회 소스 (기본: `all`)
  - `all`: NXLOG + BWS 모두 조회
  - `nxlog`: NXLOG 서비스 목록만
  - `bws`: BWS/탐지 API 서비스 목록만

예시:
```bash
# "메이플" 관련 서비스 검색
python ${CLAUDE_PLUGIN_ROOT}/service_lookup.py search "메이플"

# 특정 서비스 ID로 검색
python ${CLAUDE_PLUGIN_ROOT}/service_lookup.py search "430011909"

# BWS에 등록된 서비스만 검색
python ${CLAUDE_PLUGIN_ROOT}/service_lookup.py search "카트" --source bws

# NXLOG 전체 게임 목록에서 검색
python ${CLAUDE_PLUGIN_ROOT}/service_lookup.py search "던전앤파이터" --source nxlog

# 전체 서비스 목록 조회 (검색어 없이)
python ${CLAUDE_PLUGIN_ROOT}/service_lookup.py search
```

## 출력 해석 가이드

결과 JSON의 각 항목:
- `service_id`: 서비스 ID 값
- `name`: 게임명 또는 메모
- `source`: 출처 (`nxlog` 또는 `bws`)
- `type`: (bws만) 발급 유형 ("NXLOG 서비스ID" 또는 "임의 발급")

사용자에게 결과를 보여줄 때:
- 테이블 형태로 service_id, name, source를 정리하여 표시
- NXLOG과 BWS에 동일 서비스가 있을 수 있음 (ID는 같지만 name 표기가 다를 수 있음)
- 검색 결과가 많으면 핵심 항목만 요약

## 활용

이 스킬로 조회한 service_id를 detection-log 플러그인의 `-s` 옵션에 사용할 수 있습니다:
```bash
# service_lookup으로 서비스 ID 확인 후
python ${CLAUDE_PLUGIN_ROOT}/../detection-log/detection_log.py search -s 430011909 -f "now-1h"
```
