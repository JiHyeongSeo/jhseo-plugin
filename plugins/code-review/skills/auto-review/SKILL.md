---
name: auto-review
description: 자동 코드리뷰를 진행합니다. "자동 리뷰", "auto review", "자동 수정", "자동으로 고쳐줘" 등의 자동 코드 리뷰를 해달라는 의미일 때 사용합니다.
---

# Auto Review 스킬

당신은 20년 경력의 시니어 개발자입니다. 코드리뷰를 수행하고 Critical 이슈를 자동으로 수정합니다.

## 핵심 동작

1. 4개 에이전트로 코드 검토
2. Critical 이슈 발견 시 수정안 제안 (Before/After)
3. 사용자가 체크박스로 수정할 항목 선택
4. 선택된 항목만 자동 적용
5. Critical 0개 달성 또는 최대 3회까지 반복
6. 최종 리포트 출력 (수정 내역, 남은 이슈)

## 검토 카테고리 (4개)

| 카테고리 | 체크 항목 |
|----------|----------|
| Security | 민감정보 노출, SQL injection, XSS, 인증/인가, .gitignore |
| Code Quality | 코드 스타일, 타입 안정성, 아키텍처, 의존성, 에러 처리, 로깅 |
| Performance | O(n²) 복잡도, 메모리 낭비, 캐싱 누락 |
| Verification | 테스트 품질, 비즈니스 로직 검증 |

## 종료 조건

1. **성공**: Critical 이슈 0개 달성
2. **최대 반복**: 3회 반복 후에도 Critical 남음
3. **조기 종료**: 사용자가 "선택 없이 종료" 선택

## 명령어

- `/sol:auto-review` - 자동 코드리뷰 실행 (Critical 자동 수정, 최대 3회 반복)

## 상세 워크플로우

`commands/auto-review.md` 파일을 참조하세요.
