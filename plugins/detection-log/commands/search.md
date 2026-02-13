---
description: 탐지 API 로그를 검색합니다
---

# 탐지 로그 검색

사용자가 요청한 조건으로 Elasticsearch 탐지 로그를 검색합니다.

검색 조건: $ARGUMENTS

사용자의 요청을 분석하여 적절한 서브커맨드(search 또는 stats)와 옵션을 결정한 후 실행하세요.

## 로그 검색
```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py search $ARGUMENTS
```

## 서비스별 통계
```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats service $ARGUMENTS
```

## 탐지 타입별 통계
```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats type $ARGUMENTS
```

## 시간대별 추이
```bash
python ${CLAUDE_PLUGIN_ROOT}/detection_log.py stats timeline $ARGUMENTS
```

검색 결과를 사용자에게 읽기 쉬운 표 형태로 정리하여 보여주세요.
