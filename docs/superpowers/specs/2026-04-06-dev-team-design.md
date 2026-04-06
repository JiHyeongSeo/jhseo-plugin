# dev-team 플러그인 설계 문서

**작성일:** 2026-04-06
**플러그인명:** dev-team
**위치:** `plugins/dev-team/`

---

## 1. 개요

Builder + Validator 두 에이전트가 Agent Teams로 협업하는 개발 워크플로우 플러그인.
Builder는 설계/구현/문서화를, Validator는 독립적 컨텍스트에서 QA/코드리뷰/보안리뷰를 담당한다.
Superpowers 워크플로우의 좋은 습관(TDD, git worktree, 계획 수립)을 내부적으로 활용하고,
Sol 플러그인의 검증 에이전트들을 재사용한다.

---

## 2. 핵심 원칙

- **독립적 검증**: Validator는 Agent Teams로 별도 세션 실행 → Builder의 reasoning 편향 없음
- **스펙 우선**: 구현 전 스펙 문서 확정 → 사용자 승인 → Validator가 스펙 기준으로 QA
- **기존 자산 재사용**: 새로 만들지 않고 Superpowers 스킬, Sol 에이전트 활용
- **사용자 설정 가능**: 모델, 최대 반복 횟수를 프로젝트/유저 설정으로 오버라이드

---

## 3. 디렉토리 구조

```
plugins/dev-team/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── builder.md          # 신규: 설계 + 코드 + 문서 담당
│   ├── code-quality.md     # sol에서 복사
│   ├── security.md         # sol에서 복사
│   ├── performance.md      # sol에서 복사
│   └── verification.md     # sol에서 복사
├── skills/
│   └── dev-team/
│       └── SKILL.md        # 오케스트레이터 스킬
└── commands/
    └── dev.md              # /dev 커맨드 정의
```

---

## 4. 워크플로우

```
[Phase 0] 요구사항 수신
          오케스트레이터가 사용자 요청 분석
          → 개발 모드 / 검토 모드 분기

[개발 모드]
[Phase 1] 요구사항 명확화 (Brainstorming)
          - superpowers:brainstorming 스킬 호출
            - 질문 1개씩 순차적으로 요건 명확화
            - 대안 2-3개 탐색 및 추천
            - 설계 섹션별 사용자 확인
            - QA 관련 질문 포함:
              "어떤 테스트가 필요한가?"
              "엣지 케이스는 무엇인가?"
              "Mock을 쓸지, 실제 환경을 쓸지?"
          - 사용자 확인 대기 ← 여기서 멈춤

[Phase 2] 스펙 작성 (Builder)
          - brainstorming 결과를 기반으로 _workspace/spec.md 생성
            - 구현 기능 목록
            - 입출력 정의
            - 완료 기준 (Done Criteria)
            - 태스크 분해 (writing-plans 스킬 활용)
          - 사용자 확인 대기 ← 여기서 멈춤

[Phase 3] 구현 환경 준비
          - using-git-worktrees 스킬 호출 → 격리 브랜치 생성

[Phase 4] 구현 (Builder)
          - test-driven-development 스킬 활용 (RED→GREEN→REFACTOR)
          - 태스크 단위로 구현 + 단위 테스트 작성/실행
          - API/DB 테스트: Bash로 실행 (환경 있을 때)
          - 문서화: 변경사항 기준으로 작성

[Phase 5] 검증 루프 (Builder ↔ Validator, Agent Teams)
          Validator 실행 (독립 컨텍스트):
            [Layer 1] 스펙 준수 검증
            - _workspace/spec.md의 Done Criteria 항목을 하나씩 체크
            - 누락 기능, 입출력 불일치, 미구현 항목 식별
            - "구현됐나?" 에 대한 기능적 검증

            [Layer 2] 코드 품질 검증 (sol 에이전트 활용)
            - code-quality, security, performance, verification 순차 실행
            - "잘 만들어졌나?" 에 대한 정적 분석

            - 결과를 _workspace/review-round-N.md 에 기록
          
          종료 조건 A (통과):
            Critical/Major 이슈 없음 → Phase 5 진행
          
          종료 조건 B (한계 도달):
            maxIterations 초과 → 사용자에게 미해결 이슈 보고 후 종료
          
          이슈 있으면:
            Builder가 피드백 반영 → Validator 재실행 → 반복

[Phase 6] 완료 처리
          - finishing-a-development-branch 스킬 호출
          - 옵션 제시: PR 생성 / merge / 브랜치 유지 / worktree 정리

[검토 모드]
          Validator만 단독 실행 (Phase 4와 동일)
          기존 sol /review 와 동일한 경험 제공
```

---

## 5. 에이전트 정의

### 5-1. Builder (`agents/builder.md`)

**신규 작성**

```
역할: 설계, 구현, 문서화 전담
모델: sonnet (기본값, 설정으로 오버라이드 가능)

책임:
- 요구사항을 받아 스펙 문서 작성
- 태스크 분해 (writing-plans 스킬 활용)
- TDD 방식으로 구현 (test-driven-development 스킬 활용)
- 변경사항 기반 문서 작성
- Validator 피드백 수신 후 수정

사용 도구:
- Read, Edit, Write, Bash (테스트 실행)
- TaskCreate, TaskUpdate (진행 상황 추적)
- SendMessage (Validator와 소통)
```

### 5-2. Validator 에이전트들

**Sol 플러그인에서 복사** (`plugins/code-review/agents/` → `plugins/dev-team/agents/`)

| 파일 | 역할 | 출처 |
|------|------|------|
| `code-quality.md` | 코드 스타일, 타입 안정성, 아키텍처 | sol 복사 |
| `security.md` | 보안 취약점, 민감정보 노출 | sol 복사 |
| `performance.md` | 성능 이슈, 복잡도 | sol 복사 |
| `verification.md` | 테스트 품질, 비즈니스 로직 | sol 복사 |

Validator 오케스트레이션은 SKILL.md가 담당.
4개 에이전트를 순차 실행 후 결과 종합.

---

## 6. Superpowers 스킬 활용 계획

직접 구현하지 않고 기존 스킬을 호출하는 방식:

| Superpowers 스킬 | 활용 시점 | 호출 주체 |
|-----------------|----------|----------|
| `superpowers:brainstorming` | Phase 1 요구사항 명확화 | 오케스트레이터 |
| `superpowers:writing-plans` | Phase 2 스펙/태스크 분해 | Builder |
| `superpowers:using-git-worktrees` | Phase 3 격리 브랜치 생성 | 오케스트레이터 |
| `superpowers:test-driven-development` | Phase 4 구현 | Builder |
| `superpowers:verification-before-completion` | Phase 5 완료 전 검증 | Validator |
| `superpowers:finishing-a-development-branch` | Phase 6 완료 처리 | 오케스트레이터 |

---

## 7. 사용자 설정

### 설정 위치
- **전역**: `~/.claude.json`
- **프로젝트**: 프로젝트 `CLAUDE.md`에 명시

### 설정 항목

```json
{
  "dev-team": {
    "maxIterations": 10,
    "builderModel": "sonnet",
    "validatorModel": "sonnet"
  }
}
```

| 항목 | 기본값 | 설명 |
|------|--------|------|
| `maxIterations` | `10` | Builder-Validator 최대 반복 횟수 |
| `builderModel` | `"sonnet"` | Builder 에이전트 모델 |
| `validatorModel` | `"sonnet"` | Validator 에이전트 모델 |

모델값은 현재 Claude 계열만 지원 (`opus`, `sonnet`, `haiku`).
향후 Claude Code가 멀티모델을 지원하면 다른 모델명으로 교체 가능하도록 문자열로 관리.

---

## 8. 실행 전제 조건

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

팀원 모두 위 설정 필요. 없으면 오케스트레이터가 안내 메시지 출력 후 종료.

---

## 9. QA 범위 및 한계

**포함:**
- 스펙 충족 여부 (정적 분석)
- 코드 품질, 보안, 성능 리뷰
- 단위 테스트 작성 및 실행
- API 동작 검증 (서버 기동 시 Bash로 curl 호출)
- DB 쿼리/스키마 정적 검토

**미포함 (향후 확장):**
- 브라우저 E2E 테스트 (Playwright 연동)
- 시각적 UI 검증

---

## 10. 파일 컨벤션

작업 중 생성되는 중간 산출물:

```
_workspace/
├── spec.md                 # 스펙 + 완료 기준 (사용자 승인용)
├── plan.md                 # 태스크 분해 결과
├── review-round-1.md       # 1차 Validator 결과
├── review-round-2.md       # 2차 Validator 결과
└── ...
```

### spec.md 필수 포함 항목

```markdown
## 구현 기능 목록
- 기능 A: ...
- 기능 B: ...

## 입출력 정의
- API: POST /xxx → 200/400/401
- 데이터 모델: ...

## Done Criteria (Validator 체크리스트)
- [ ] 항목 1 (구체적이고 검증 가능하게)
- [ ] 항목 2
- [ ] 항목 3

## QA 계획
### 테스트 범위
- 단위 테스트: 어떤 함수/모듈을 테스트할지
- 통합 테스트: API 엔드포인트, DB 연동 등
- 제외 범위: 테스트하지 않는 부분과 이유

### 엣지 케이스
- 입력 경계값, 예외 상황, 실패 시나리오

### 테스트 환경
- Mock 사용 여부 (DB, 외부 API 등)
- 필요한 픽스처/시드 데이터

### 커버리지 목표
- 최소 커버리지 기준 (예: 핵심 비즈니스 로직 80% 이상)
```

Done Criteria와 QA 계획은 Brainstorming 단계에서 사용자와 함께 구체화.
Validator Layer 1은 Done Criteria + QA 계획을 모두 기준으로 검증:
- 기능이 구현됐는지
- 합의한 테스트가 작성됐는지
- 엣지 케이스가 커버됐는지

---

## 11. marketplace.json 업데이트

`plugins/dev-team` 을 marketplace.json의 `plugins` 배열에 추가:

```json
{
  "name": "dev-team",
  "source": "./plugins/dev-team",
  "description": "Builder + Validator Agent Teams 기반 개발 워크플로우. 스펙 작성 → TDD 구현 → 독립 검증 루프",
  "version": "1.0.0",
  "author": { "name": "SOL Team" },
  "keywords": ["agent-teams", "builder", "validator", "dev-workflow", "tdd", "code-review"],
  "category": "development"
}
```

---

## 12. 미결 사항

- [ ] `commands/dev.md` 트리거 키워드 확정
- [ ] Validator가 스펙 기준 QA 시 사용할 체크리스트 포맷 확정
- [ ] maxIterations 도달 시 사용자 보고 포맷

