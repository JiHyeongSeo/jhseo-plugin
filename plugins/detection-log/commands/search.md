---
description: 탐지 API 로그를 검색합니다
---

# 탐지 로그 검색

사용자의 요청: $ARGUMENTS

**중요:** 사용자의 자연어 요청을 아래 CLI 옵션으로 변환하여 실행하세요. `$ARGUMENTS`를 그대로 CLI에 넘기면 안 됩니다.

## 옵션 변환 예시

| 사용자 요청 | CLI 변환 |
|---|---|
| "마비노기 모바일의 badword_kor 탐지된 텍스트 10개" | `search -s {serviceId} --type badword_kor --detected -n 10` |
| "마비노기 모바일의 badword_kor 미탐 건수 100개" | `search -s {serviceId} --type badword_kor --undetected -n 100` |
| "최근 24시간 서비스별 통계" | `stats service -f "now-24h"` |
| "badword_kor 탐지율" | `stats type --type badword_kor` |
| "최근 7일 시간대별 추이" | `stats timeline -f "now-7d"` |

## 서비스명이 언급된 경우

서비스명(예: "마비노기 모바일", "메이플스토리")이 포함된 요청은 먼저 service-lookup으로 serviceId를 조회하세요:
```bash
python ${CLAUDE_PLUGIN_ROOT}/../service-lookup/service_lookup.py search "서비스명"
```

## stats service 결과에 서비스명 붙이기

`stats service` 결과의 서비스 ID들을 `batch` 명령으로 한 번에 조회하세요 (개별 조회 금지):
```bash
python ${CLAUDE_PLUGIN_ROOT}/../service-lookup/service_lookup.py batch ID1 ID2 ID3 ...
```

## CLI 실행

```bash
# 로그 검색
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search [옵션]

# 서비스별 통계
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats service [옵션]

# 탐지 타입별 통계
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats type [옵션]

# 시간대별 추이
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats timeline [옵션]
```

검색 결과를 사용자에게 읽기 쉬운 표 형태로 정리하여 보여주세요.
