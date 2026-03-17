---
name: service-lookup
description: 서비스 ID 조회. 게임명이나 메모로 BWS 및 NXLOG 서비스 ID를 검색할 때 사용합니다. "서비스 ID", "서비스 검색", "게임 서비스" 등의 키워드에서 활성화됩니다.
---

# Service Lookup 스킬

게임명이나 메모로 서비스 ID를 검색하는 스킬입니다. 기존 클로드 전용 플러그인과 동일하게 동작합니다.

## 실행 방법
이 스킬이 트리거되면, Gemini 에이전트는 사용자의 요청을 분석하여 이 `SKILL.md` 파일과 **동일한 디렉토리**에 위치한 `service_lookup.py` 파이썬 스크립트를 실행해야 합니다. 

**명령어 포맷:**
```bash
python $(dirname "$BASH_SOURCE")/service_lookup.py search "검색어" [--source all|nxlog|bws]
```
*(참고: Gemini CLI에서는 스킬 폴더의 절대 경로를 활용하여 스크립트를 실행할 수 있습니다. 위 예시처럼 실행 환경에 맞게 경로를 지정하여 실행하세요.)*

### 옵션
- `검색어`: 게임명, 메모, 서비스 ID 중 일부 (대소문자 무관)
- `--source`: 조회 소스 (기본: `all`)
  - `all`: NXLOG + BWS 모두 조회
  - `nxlog`: NXLOG 서비스 목록만
  - `bws`: BWS/탐지 API 서비스 목록만

### 예시
```bash
# "메이플" 관련 서비스 검색
python <절대경로>/service_lookup.py search "메이플"

# BWS에 등록된 서비스만 검색
python <절대경로>/service_lookup.py search "카트" --source bws
```

## 환경 변수
원활한 동작을 위해 환경에 다음 변수가 설정되어 있어야 합니다:
- `NXLOG_SERVICE_USER`
- `NXLOG_SERVICE_PASSWORD`
- `INFERENCE_API_KEY`