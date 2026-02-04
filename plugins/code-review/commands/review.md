---
name: review
description: 현재 staged 파일에 대해 수동으로 코드리뷰 실행
user_invocable: true
---

# 수동 코드리뷰

staged 파일에 대해 AI 코드리뷰를 수행합니다.

## 지시사항

1. `git diff --staged` 명령으로 staged 변경사항 확인
2. `git diff --staged --name-only`로 변경된 파일 목록 확인
3. 각 파일의 전체 내용을 `git show :파일명`으로 읽기
4. `.gitignore` 내용 확인

## 리뷰 기준

### 카테고리별 체크
1. **Type Safety**: 타입 안정성, any 남용, 타입 추론 이슈
2. **Readability**: 가독성, 네이밍, 코드 구조
3. **Security**: 민감정보 노출, SQL injection, XSS 등
4. **Performance**: 시간복잡도 O(n²) 이상, 불필요한 연산, 메모리 낭비
5. **Database**: N+1 쿼리, 인덱스 미사용, 트랜잭션 이슈
6. **Architecture**: DTO 구조, 중복 코드 (3회 이상), 책임 분리
7. **Gitignore**: 민감 파일(.env, credentials, *.key 등)이 .gitignore에 포함되어 있는지

### 심각도 분류
- **Critical**: 즉시 수정 (보안, 심각한 버그)
- **Major**: 수정 권장 (성능, 타입 이슈)
- **Minor**: 개선 제안 (가독성, 리팩토링)

### 필수 vs 선택 구분
- **🔴 필수 (MUST FIX)**: 프로덕션 배포 전 반드시 수정
- **🟡 권장 (SHOULD FIX)**: 코드 품질 향상
- **🔵 선택 (NICE TO HAVE)**: 시간 여유 있을 때

## 출력 형식

### 요약
- 전체 이슈 수
- 필수/권장/선택 개수
- 총평

### 이슈 목록
각 이슈에 대해:
- [심각도] 카테고리 - [필수/권장/선택]
- 파일명:라인번호
- 문제점 설명
- Before/After 코드 블록
- 우선순위 (1-5)

### 시니어 한마디
실무 관점 총평과 조언
