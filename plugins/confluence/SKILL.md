---
name: confluence
description: Confluence 페이지 검색/조회/생성/수정. "confluence", "컨플루언스", "컨플", "문서 생성", "페이지 검색", "배포 노트" 등의 키워드에서 활성화
---

# Confluence 스킬

Confluence 페이지를 검색, 조회, 생성, 수정하는 스킬입니다. 기존 클로드 전용 플러그인과 동일하게 동작합니다.

## 실행 지침 (For Gemini Agent)
Gemini 에이전트는 사용자의 요청을 분석하여 이 `SKILL.md` 파일과 **동일한 디렉토리**에 위치한 `confluence.py` 파이썬 스크립트를 실행해야 합니다.

명령어 실행 전 상세한 옵션 및 환경변수(CONFLUENCE_API_TOKEN 등) 확인이 필요하다면 `skills/confluence/SKILL.md` 파일을 읽고 지침을 따르세요.

**명령어 포맷:**
```bash
python $(dirname "$BASH_SOURCE")/confluence.py [명령어] [옵션]
```
*(참고: 클로드 코드의 `$CLAUDE_PLUGIN_ROOT` 환경변수 대신, 현재 스킬 폴더의 절대경로를 기반으로 스크립트를 직접 찾아서 실행하세요.)*