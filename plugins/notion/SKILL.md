---
name: notion
description: Notion 페이지 검색/조회/생성/수정. "notion", "노션", "문서 생성", "페이지 검색", "배포 노트", "아키텍처", "회의록", "트러블슈팅", "ADR" 등의 키워드에서 활성화
---

# Notion 스킬

Notion 페이지를 검색, 조회, 생성, 수정하는 스킬입니다. 기존 Confluence 플러그인의 Notion 전환 버전입니다.

## 실행 지침 (For Gemini Agent)
Gemini 에이전트는 사용자의 요청을 분석하여 `skills/notion/SKILL.md` 파일을 읽고 지침을 따르세요.

Notion MCP 도구(`notionApi`)를 직접 호출하여 동작합니다. 별도 CLI 스크립트가 필요하지 않습니다.
