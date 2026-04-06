---
name: dev-team
description: "개발팀 오케스트레이터. 만들어줘, 구현해줘, 개발해줘, 기능 추가, 리뷰해줘, 코드리뷰, 검토해줘, review 키워드에서 활성화. Builder-Validator 루프를 통한 자동 개발 및 코드 검토."
---

# Dev-Team Orchestrator

사용자의 요청을 받아 Builder-Validator 팀을 오케스트레이션하여 개발 또는 검토를 수행한다.

---

## 설정값 읽기

아래 순서로 설정을 읽어 나중에 읽은 값이 앞의 값을 덮어쓴다.

### Step 1: 기본값

```
maxIterations = 10
builderModel  = "sonnet"
validatorModel = "sonnet"
```

### Step 2: ~/.claude.json

```bash
cat ~/.claude.json 2>/dev/null
```

파일이 존재하면 JSON에서 `dev-team` 키 아래의 값을 읽어 기본값을 덮어쓴다.

```json
{
  "dev-team": {
    "maxIterations": 5,
    "builderModel": "opus",
    "validatorModel": "sonnet"
  }
}
```

### Step 3: 프로젝트 CLAUDE.md

```bash
cat CLAUDE.md 2>/dev/null
```

CLAUDE.md에 `dev-team` 섹션이 있으면 해당 값으로 다시 덮어쓴다. 형식 예시:

```markdown
## dev-team
- maxIterations: 3
- builderModel: opus
- validatorModel: opus
```

**최종 설정값을 확인한 뒤 Phase 0으로 진행한다.**

---

## Phase 0: 모드 감지

사용자의 메시지를 분석하여 모드를 결정한다.

### 개발 모드 (Phase 1-6 실행)

다음 키워드가 포함된 경우:
- 만들어줘, 구현해줘, 개발해줘, 기능 추가
- 새로운 기능/모듈/컴포넌트/API 관련 요청
- 버그 수정 요청

### 검토 모드 (Phase 5만 실행)

다음 키워드가 포함된 경우:
- 리뷰해줘, 코드리뷰, 검토해줘, review
- 기존 코드에 대한 품질 점검 요청

**모드 판별이 애매한 경우** 사용자에게 물어본다:

```
개발(구현)과 검토(코드리뷰) 중 어떤 작업을 원하시나요?
1. 개발 모드 — 브레인스토밍 → 스펙 → 구현 → 검증
2. 검토 모드 — 기존 코드를 리뷰
```

---

# [개발 모드] Phase 1-6

---

## Phase 1: 브레인스토밍

`skills/dev-team/brainstorming.md` 스킬의 프로세스를 따른다.

**핵심:**
1. 프로젝트 컨텍스트 파악 (파일, docs, 최근 커밋)
2. 한 번에 하나씩 질문하여 요구사항 구체화
3. 2-3가지 접근법 제안 및 추천
4. 설계를 섹션별로 제시하고 사용자 승인 확인
5. **반드시 포함할 추가 질문:**
   - QA 계획: 필요한 테스트 종류, 엣지 케이스, 테스트 환경 (Mock vs 실제)
   - 문서화: 필요 여부, 작성 위치 (로컬 README / Confluence / Notion / 해당없음)

**Phase 1 완료 조건:** 사용자가 설계를 승인함.

---

## Phase 2: 스펙 작성 및 승인

### Step 1: Builder가 `_workspace/spec.md` 작성

브레인스토밍 결과를 기반으로 다음 섹션을 모두 포함하는 스펙을 작성한다:

```markdown
# [기능명] 스펙

## 1. 구현 기능 목록
- 기능 A: 설명
- 기능 B: 설명
- ...

## 2. 입출력 정의
### 입력
- 파라미터/인터페이스 정의

### 출력
- 반환값/응답 형식 정의

## 3. Done Criteria
모든 항목이 충족되어야 구현 완료로 판정한다.
- [ ] 기능 A가 정상 동작한다
- [ ] 기능 B가 정상 동작한다
- [ ] 단위 테스트가 모두 통과한다
- [ ] 에러 케이스가 처리된다
- [ ] ...

## 4. 문서화 계획
- 작성 대상: (README / Confluence / Notion / 해당없음)
- 문서 범위: (API 문서 / 사용 가이드 / 아키텍처 설명 등)

## 5. QA 계획
- 테스트 종류: (단위 / 통합 / API / E2E)
- 엣지 케이스 목록:
  - ...
- 테스트 환경: (Mock / 실제 DB / 실제 서버)
```

### Step 2: 사용자에게 승인 요청

스펙을 작성한 뒤 다음 메시지를 출력하고 **반드시 사용자 응답을 기다린다:**

```
📋 스펙을 작성했습니다: `_workspace/spec.md`

내용을 확인해주세요. 수정이 필요하면 말씀해주시고,
괜찮으면 "승인" 또는 "진행"이라고 답해주세요.
```

- 사용자가 수정을 요청하면 스펙을 수정하고 다시 승인을 요청한다.
- 사용자가 승인하면 Phase 3으로 진행한다.

**사용자가 명시적으로 승인하기 전까지 Phase 3 이후를 절대 실행하지 않는다.**

---

## Phase 3: Git Worktree 설정

`skills/dev-team/git-worktrees.md` 스킬의 프로세스를 따른다.

1. 워크트리 디렉토리 탐색 (기존 > CLAUDE.md > 사용자 질문)
2. .gitignore 검증 (프로젝트 로컬인 경우)
3. 워크트리 생성 및 브랜치 생성
4. 프로젝트 의존성 설치
5. 베이스라인 테스트 실행

```bash
git worktree add <worktree-path> -b <branch-name>
cd <worktree-path>
# 프로젝트 의존성 설치 (auto-detect)
# 베이스라인 테스트 실행
```

**Phase 3 완료 조건:** 워크트리가 생성되고 베이스라인 테스트가 통과함.

---

## Phase 4: TDD 구현

### Step 1: 구현 계획 작성

`skills/dev-team/writing-plans.md` 스킬을 따라 `_workspace/plan.md`를 작성한다.

- `_workspace/spec.md`의 Done Criteria와 QA 계획을 태스크로 분해
- 각 태스크는 2-5분 단위의 작은 스텝으로 구성
- 파일 구조, 정확한 경로, 코드 블록 포함

### Step 2: Builder 에이전트로 구현 실행

`skills/dev-team/tdd.md` 가이드를 따라 TDD로 구현한다.

- Red-Green-Refactor 사이클 준수
- 스펙의 QA 계획 섹션에 정의된 엣지 케이스를 TDD 사이클에 반영
- 기능 단위로 작게 커밋
- 모든 테스트가 통과하는 상태를 유지

**Phase 4 완료 조건:** `_workspace/plan.md`의 모든 태스크가 구현되고 전체 테스트가 통과함.

---

## Phase 5: Validator 검증 루프

**이 Phase가 dev-team의 핵심이다.** Builder가 구현한 코드를 Validator가 검증하고, 이슈가 있으면 Builder가 수정하는 루프를 반복한다.

### 변수 초기화

```
currentRound = 1
```

### 루프 시작

다음을 `currentRound <= maxIterations` 동안 반복한다:

---

#### Layer 1: 스펙 Done Criteria 검증

**`_workspace/spec.md`가 존재하는 경우에만 실행한다.**

Validator 팀을 Agent Teams로 스폰하여 다음을 수행한다:

1. `_workspace/spec.md`의 **Done Criteria** 섹션을 읽는다
2. 체크리스트 항목을 **하나씩** 검증한다:
   - 해당 기능이 구현되어 있는가?
   - 관련 테스트가 존재하고 통과하는가?
   - 엣지 케이스가 처리되어 있는가?
3. 각 항목의 결과를 PASS / FAIL로 기록한다

**Layer 1 결과를 임시로 보관하고 Layer 2로 진행한다.**

---

#### Layer 2: 코드 품질 검증

다음 4개 에이전트를 **순차적으로** 실행한다:

**2-1. Code Quality** (`agents/code-quality.md`)
- 코드 스타일, 타입 안정성, 아키텍처, 의존성, 에러 처리, 로깅 검사

**2-2. Security** (`agents/security.md`)
- 민감정보 노출, Injection, XSS, 인증/인가, .gitignore 검사

**2-3. Performance** (`agents/performance.md`)
- 시간 복잡도, 불필요한 연산, 메모리 낭비, 캐싱 누락 검사

**2-4. Verification** (`agents/verification.md`)
- 테스트 품질, 비즈니스 로직, 엣지 케이스, 동시성 이슈 검사

각 에이전트는 이슈를 `Critical / Major / Minor` 심각도로 분류한다.

---

#### 결과 기록

Layer 1 + Layer 2 결과를 합쳐 `_workspace/review-round-N.md`에 기록한다:

```markdown
# Review Round N

## Layer 1: 스펙 Done Criteria 검증
| # | Done Criteria 항목 | 결과 | 비고 |
|---|-------------------|------|------|
| 1 | 기능 A가 정상 동작 | PASS | - |
| 2 | 단위 테스트 통과   | FAIL | 2개 테스트 미작성 |

## Layer 2: 코드 품질 검증

### Code Quality
(이슈 목록 또는 "이슈 없음")

### Security
(이슈 목록 또는 "이슈 없음")

### Performance
(이슈 목록 또는 "이슈 없음")

### Verification
(이슈 목록 또는 "이슈 없음")

## 종합 판정
- Critical 이슈: N개
- Major 이슈: N개
- Minor 이슈: N개
- **판정: PASS / FAIL**
```

---

#### 종료 조건 판정

**Exit A — PASS:**
- Layer 1의 모든 항목이 PASS이고
- Layer 2에 Critical 또는 Major 이슈가 0개

이 경우 Phase 6으로 진행한다.

**Exit B — maxIterations 도달:**
- `currentRound > maxIterations`

이 경우 사용자에게 다음을 보고하고 **중단한다:**

```
⚠️ 최대 검증 횟수(N회)에 도달했습니다.

미해결 이슈:
- [Critical/Major 이슈 목록]

검토 이력: _workspace/review-round-1.md ~ _workspace/review-round-N.md

추가 지시를 기다립니다.
```

**FAIL — 이슈 발견:**
- Critical 또는 Major 이슈가 존재하는 경우

Builder에게 수정을 지시한다:

1. `_workspace/review-round-N.md`를 Builder에게 전달
2. Builder가 Critical/Major 이슈를 수정
3. Builder가 수정 완료를 보고
4. `currentRound += 1`
5. 루프 처음으로 돌아감 (Layer 1부터 재실행)

---

## Phase 6: 브랜치 완료

`skills/dev-team/finishing.md` 스킬의 프로세스를 따른다.

1. 전체 테스트 실행 및 통과 확인
2. base branch 확인
3. 사용자에게 4가지 옵션 제시:
   - 로컬 머지
   - PR 생성
   - 브랜치 유지
   - 작업 폐기
4. 선택에 따라 실행
5. 워크트리 정리 (옵션에 따라)

**Phase 6 완료 = 개발 모드 종료.**

---

# [검토 모드]

기존 코드를 리뷰만 수행한다. 구현 없이 Phase 5(검증 루프)만 실행한다.

## 진입 조건 확인

```bash
ls _workspace/spec.md 2>/dev/null
```

### `_workspace/spec.md`가 존재하는 경우
- Layer 1 (스펙 Done Criteria 검증) + Layer 2 (코드 품질 검증) 모두 실행

### `_workspace/spec.md`가 존재하지 않는 경우
- Layer 1을 **건너뛰고** Layer 2 (코드 품질 검증)만 실행

## 실행

Phase 5의 검증 루프를 실행하되, **Builder 수정 단계를 생략**한다.

1. Layer 1 (해당 시) + Layer 2 실행
2. 결과를 `_workspace/review-round-1.md`에 기록
3. 결과를 사용자에게 보고

```
📝 코드 리뷰 완료: `_workspace/review-round-1.md`

[Critical/Major/Minor 이슈 요약]

수정이 필요하면 "수정해줘"라고 말씀해주세요.
개발 모드로 전환하여 자동 수정을 진행합니다.
```

사용자가 "수정해줘"라고 요청하면 개발 모드 Phase 4(구현)부터 시작하되, 기존 리뷰 결과를 Builder에게 전달하여 수정을 진행한다.

---

# Workspace 파일 규약

| 파일 | 용도 |
|------|------|
| `_workspace/spec.md` | 스펙 + Done Criteria |
| `_workspace/plan.md` | 구현 태스크 분해 |
| `_workspace/review-round-N.md` | N번째 검증 결과 (N = 1, 2, 3, ...) |

- `_workspace/` 디렉토리는 프로젝트 루트(또는 워크트리 루트)에 생성한다.
- `.gitignore`에 `_workspace/`가 포함되어 있지 않으면 추가한다.

---

# Agent Teams 스폰 규약

## Builder 스폰

```
Builder 에이전트를 스폰한다:
- 에이전트 정의: agents/builder.md
- 모델: {builderModel}
- 전달 컨텍스트:
  - 사용자 요구사항
  - _workspace/spec.md
  - _workspace/plan.md (Phase 4 이후)
  - _workspace/review-round-N.md (수정 시)
```

## Validator 스폰

```
Validator를 구성하는 에이전트들을 순차 스폰한다:
- 모델: {validatorModel}
- 에이전트 순서:
  1. agents/code-quality.md
  2. agents/security.md
  3. agents/performance.md
  4. agents/verification.md
- 전달 컨텍스트:
  - _workspace/spec.md (존재 시)
  - 변경된 파일 목록 (git diff)
```

---

# 오케스트레이터 행동 원칙

1. **사용자 승인 없이 다음 Phase로 넘어가지 않는다** (Phase 2 → 3 전환 시 반드시 승인)
2. **Agent Teams 없이 Builder/Validator를 직접 실행하지 않는다**
3. **maxIterations를 초과하여 루프를 실행하지 않는다**
4. **검토 모드에서 코드를 직접 수정하지 않는다** (사용자 요청 시에만 개발 모드 전환)
5. **각 Phase 완료 시 사용자에게 진행 상황을 보고한다**
6. **에러 발생 시 해당 Phase에서 멈추고 사용자에게 보고한다**
