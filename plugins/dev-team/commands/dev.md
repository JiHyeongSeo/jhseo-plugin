---
name: dev
description: dev-team 워크플로우 실행. 개발 모드(구현 요청)와 검토 모드(리뷰 요청)를 자동 분기합니다.
---

# /dev 커맨드

dev-team 플러그인의 진입점입니다.

## 사용법

```
/dev [요청 내용]
```

## 예시

```
/dev 로그인 기능 만들어줘
/dev 현재 변경사항 리뷰해줘
/dev POST /api/users 엔드포인트 추가해줘
```

## 동작

`skills/dev-team/SKILL.md` 오케스트레이터를 실행합니다.
요청 내용에 따라 개발 모드 또는 검토 모드로 자동 분기됩니다.
