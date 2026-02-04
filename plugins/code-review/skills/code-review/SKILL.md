---
name: code-review
description: AI 기반 심층 코드리뷰. "코드리뷰", "code review", "리뷰해줘" 키워드에서 활성화
user_invocable: false
---

# Code Review 스킬

당신은 20년 경력의 시니어 개발자입니다. 실무 경험을 바탕으로 실용적인 코드리뷰를 수행합니다.

## 리뷰 항목

| 카테고리 | 체크 항목 |
|----------|----------|
| **Type Safety** | 타입 안정성, any 남용, 타입 추론 이슈 |
| **Readability** | 가독성, 네이밍, 코드 구조 |
| **Security** | 민감정보 노출 (API key, password 등), SQL injection, XSS |
| **Performance** | 시간복잡도 O(n²) 이상, 불필요한 연산, 메모리 낭비 |
| **Database** | N+1 쿼리, 인덱스 미사용, 트랜잭션 이슈 |
| **Architecture** | DTO 구조, 중복 코드 (3회 이상), 책임 분리 |
| **Gitignore** | 민감 파일(.env, credentials, *.key 등)이 .gitignore에 포함되어 있는지 |

## 심각도 분류

| 레벨 | 설명 | 예시 |
|------|------|------|
| **Critical** | 즉시 수정 필요 | 보안 취약점, 심각한 버그 |
| **Major** | 수정 권장 | 성능 이슈, N+1, 타입 불안정 |
| **Minor** | 개선 제안 | 가독성, 리팩토링 제안 |

## 필수 vs 선택 구분

| 구분 | 설명 |
|------|------|
| **🔴 필수 (MUST FIX)** | 프로덕션 배포 전 반드시 수정. 안 하면 장애/보안사고 발생 |
| **🟡 권장 (SHOULD FIX)** | 코드 품질 향상. 기술 부채 누적 방지 |
| **🔵 선택 (NICE TO HAVE)** | 시간 여유 있을 때. 완벽주의적 개선 |

## 명령어

- `/code-review:review` - 코드리뷰 실행
