---
name: code-review
description: Git commit 시 자동 AI 코드리뷰. "코드리뷰", "code review", "리뷰" 키워드에서 활성화
user_invocable: false
---

# Code Review 스킬

Git commit 전에 AI 기반 심층 코드리뷰를 수행합니다.

## 자동 동작

`git commit` 명령 실행 시 자동으로 코드리뷰가 트리거됩니다.

## 리뷰 항목

| 카테고리 | 체크 항목 |
|----------|----------|
| **Type Safety** | 타입 안정성, 타입 이슈 |
| **Readability** | 가독성, 코드 구조 |
| **Security** | 민감정보 노출 (API key, password 등) |
| **Performance** | 시간복잡도, 불필요한 연산, 메모리 사용량 |
| **Database** | N+1 문제, 쿼리 최적화 |
| **Architecture** | DTO 구조, 중복 코드 (3회 이상) |

## 심각도 분류

| 레벨 | 설명 | 예시 |
|------|------|------|
| **Critical** | 즉시 수정 필요 | 보안 취약점, 심각한 버그 |
| **Major** | 수정 권장 | 성능 이슈, N+1, 타입 불안정 |
| **Minor** | 개선 제안 | 가독성, 리팩토링 제안 |

## 필수 vs 선택 구분

| 구분 | 설명 |
|------|------|
| **🔴 필수 (MUST FIX)** | 프로덕션 배포 전 반드시 수정 |
| **🟡 권장 (SHOULD FIX)** | 코드 품질 향상을 위해 수정 권장 |
| **🔵 선택 (NICE TO HAVE)** | 시간 여유 있을 때 개선 |

## 명령어

- `/code-review:review` - 수동 리뷰 실행
