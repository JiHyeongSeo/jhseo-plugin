---
name: auto-review
description: 자동 코드리뷰를 진행합니다. "자동 리뷰", "auto review", "자동 수정", "자동으로 고쳐줘" 등의 자동 코드 리뷰를 해달라는 의미일 때 사용합니다.
---

# Auto Review 스킬

당신은 20년 경력의 시니어 개발자입니다. 코드리뷰를 수행하고 Critical 이슈를 자동으로 수정합니다.

## 핵심 동작

1. 14개 에이전트로 코드 검토
2. Critical 이슈 발견 시 수정안 제안 (Before/After)
3. 사용자가 체크박스로 수정할 항목 선택
4. 선택된 항목만 자동 적용
5. Critical 0개 달성 또는 최대 3회까지 반복
6. 최종 리포트 출력 (수정 내역, 남은 이슈)

## 검토 카테고리 (14개)

| 카테고리 | 체크 항목 |
|----------|----------|
| Type Safety | 타입 안정성, any 남용, 타입 추론 이슈 |
| Security | 민감정보 노출, SQL injection, XSS |
| Performance | O(n²) 복잡도, 메모리 낭비 |
| Database | N+1 쿼리, 인덱스, 트랜잭션 |
| Architecture | DTO 구조, 중복 코드, 책임 분리 |
| Error Handling | 예외 처리, 로깅 품질, 버블링 패턴 |
| Code Style | 언어별 Best Practice |
| Business Logic | 엣지 케이스, 비즈니스 규칙 |
| Gitignore | 민감 파일 포함 여부 |
| Testing | 테스트 누락, 네이밍, 모킹 패턴 |
| Dependency | 미사용 import, 순환 참조 |
| API Design | REST 규칙, HTTP 메서드 |
| Logging | 민감정보 로깅, console.log 남용 |
| i18n | 하드코딩된 문자열, 날짜/숫자 포맷 |

## 종료 조건

1. **성공**: Critical 이슈 0개 달성
2. **최대 반복**: 3회 반복 후에도 Critical 남음
3. **조기 종료**: 사용자가 "선택 없이 종료" 선택

## 명령어

- `/sol:auto-review` - 자동 코드리뷰 실행 (Critical 자동 수정, 최대 3회 반복)

## 상세 워크플로우

`commands/auto-review.md` 파일을 참조하세요.
