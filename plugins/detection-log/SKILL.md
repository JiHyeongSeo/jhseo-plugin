---
name: detection-log
description: 텍스트탐지/이미지탐지 API 로그 조회 및 탐지 현황 분석. "텍스트탐지 로그", "이미지탐지 로그", "탐지 로그", "로그 검색", "탐지 현황" 등의 키워드에서 활성화
---

# Detection Log 스킬

Elasticsearch(plex)에서 텍스트탐지/이미지탐지 API 호출 로그를 검색하고 탐지 현황 및 통계를 분석하는 스킬입니다.

## 실행 지침 (For Gemini Agent)
Gemini 에이전트는 사용자의 요청을 분석하여 이 `SKILL.md` 파일과 **동일한 디렉토리**에 위치한 `detection_log.py` 파이썬 스크립트를 실행해야 합니다.

명령어 실행 전 상세한 CLI 옵션 및 환경변수(ES_USER, ES_PASSWORD 등) 확인이 필요하다면 `skills/detection-log/SKILL.md` 파일을 읽고 지침을 엄격히 따르세요.

**명령어 포맷:**
```bash
python $(dirname "$BASH_SOURCE")/detection_log.py [명령어] [옵션]
```
*(참고: 클로드 코드의 `$CLAUDE_PLUGIN_ROOT` 환경변수 대신, 현재 스킬 폴더의 절대경로를 기반으로 스크립트를 직접 찾아서 실행하세요.)*