# Smart Tag Plugin

대화형으로 Git 태그를 생성하고, Confluence 패치 노트를 자동으로 작성하는 Claude Code 플러그인입니다.

## 특징

- 🎯 **대화형 워크플로우**: 커밋 선택부터 태그 생성까지 Claude와 대화하며 진행
- 📝 **자동 문서 생성**: 태그 생성과 동시에 Confluence 릴리즈 노트 자동 작성
- 📊 **상세한 릴리즈 노트**: 커밋 히스토리 + 파일별 상세 변경 내용 (git diff 포함)
- 🔄 **버전별 관리**: 같은 버전은 하나의 문서로 관리, 환경별 배포 이력 추적
- 🏷️ **유연한 태그 형식**: 다양한 태그 형식 지원 (환경-버전, 버전만, 커스텀 등)
- 🌐 **범용 지원**: 모든 Git 저장소에서 사용 가능
- ⚡ **간단한 사용**: `/smart-tag:tag` 명령 하나로 모든 작업 완료

## 사전 요구사항

- Python 3.8 이상
- Git 레포지토리
- Confluence API Token
- [confluence 플러그인](../confluence) 설치

## 설치

### 1. 환경 변수 설정

```bash
export CONFLUENCE_API_TOKEN="your-bearer-token"
```

### 2. 플러그인 설치

```bash
claude plugin install /home/seoji/local/claude-plugins/plugins/smart-tag
```

## 사용 방법

### 기본 사용 (대화형)

```
사용자: /smart-tag:tag

Claude: 최근 10개 커밋을 보여드릴게요
        [커밋 목록 표시]

        어느 커밋에 태그를 달까요?

사용자: 맨 위 커밋

Claude: 생성할 태그명을 입력하세요
        (예: dev-v1.2.3, v1.2.3, 1.0.0, release-1.2.3)

사용자: dev-v1.2.3

Claude: dev-v1.2.3 태그를 생성하고 릴리즈 노트를 작성하시겠어요?

사용자: 네

Claude: ✓ 태그 생성 완료: dev-v1.2.3
        ✓ 릴리즈 노트 생성 중...
        ✓ 완료!

        📄 릴리즈 노트: https://confluence.../1234568
```

### 빠른 사용 (태그 지정)

```
사용자: /smart-tag:tag dev-v1.2.3

Claude: HEAD 커밋에 dev-v1.2.3 태그를 생성하시겠어요?

사용자: 네

Claude: [태그 생성 + 문서 자동 생성]

사용자: /smart-tag:tag v2.0.0

Claude: HEAD 커밋에 v2.0.0 태그를 생성하시겠어요?

사용자: 네

Claude: [태그 생성 + 문서 자동 생성]
```

## 워크플로우

```
1. 사용자: /smart-tag:tag 입력
   ↓
2. Claude: 최근 커밋 목록 표시
   ↓
3. Claude: 대화형 질문
   - 어느 커밋에 태그?
   - 태그명은? (예: dev-v1.2.3, v1.2.3, 1.0.0 등)
   ↓
4. Claude: git tag 생성
   사용자가 입력한 태그명으로 생성
   ↓
5. Claude: deployment.py 자동 실행
   - 릴리즈 노트 생성
   ↓
6. Claude: Confluence URL 출력
```

## 태그 형식

다양한 태그 형식을 유연하게 지원합니다:

**환경별 배포 태그**:
```
{환경}-v{버전}
```
- 예시: `dev-v1.0.0`, `stage-v1.2.3`, `prod-v2.0.0`
- 환경: `dev`, `stage`, `prod` 등 자유롭게 설정 가능

**단순 버전 태그**:
```
v{버전} 또는 {버전}
```
- 예시: `v1.2.3`, `v2.0.0`, `1.0.0`, `0.0.1`

**커스텀 접두사**:
```
{접두사}-{버전}
```
- 예시: `release-1.2.3`, `api-v1.0.0`

모든 Git 저장소에서 프로젝트의 태그 규칙에 맞춰 자유롭게 사용할 수 있습니다.

## 생성되는 문서

태그 생성 시 **릴리즈 노트**가 Confluence에 자동으로 생성됩니다.

### 릴리즈 노트

**위치**: 사용자가 선택한 Confluence 페이지 하위
**제목**: `{태그명} 릴리즈 노트` (예: `v1.2.3 릴리즈 노트`, `dev-v1.2.3 릴리즈 노트`)

**포함 내용**:
- 배포 이력 테이블 (환경별 배포 일시, 환경별 태그인 경우)
- 버전 정보
- 전체 커밋 히스토리
- **파일별 상세 변경 내용** (git diff 포함)
  - 추가된 파일
  - 수정된 파일
  - 삭제된 파일

## 버전별 단일 문서 관리

같은 버전은 환경에 관계없이 **하나의 문서**로 관리됩니다.

### 예시: v1.2.3 배포 과정

```
1. dev 환경 배포
   $ /smart-tag:tag dev-v1.2.3
   → 새 문서 생성

2. stage 환경 배포
   $ /smart-tag:tag stage-v1.2.3
   → 기존 문서에 배포 이력 추가

3. prod 환경 배포
   $ /smart-tag:tag prod-v1.2.3
   → 기존 문서에 배포 이력 추가
```

### 최종 배포 이력 테이블

| 환경 | 배포 일시 |
|------|-----------|
| 개발 (dev) | 2026-02-04 10:00 |
| 스테이징 (stage) | 2026-02-05 14:00 |
| 운영 (prod) | 2026-02-10 09:00 |

## Confluence 문서 구조 예시

릴리즈 노트는 프로젝트별로 원하는 공간에 자유롭게 생성할 수 있습니다.

```
프로젝트 공간
└── 릴리즈 노트 페이지
    ├── v1.2.3 릴리즈 노트
    ├── v1.2.0 릴리즈 노트
    ├── dev-v1.1.0 릴리즈 노트
    └── ...
```

대화형 모드에서 관련 페이지를 자동으로 검색하고 추천해줍니다.

## 지원 레포지토리

모든 Git 저장소에서 사용할 수 있습니다.

### 레포지토리별 설정 (선택사항)

[deployment.py](skills/tag/deployment.py)의 `REPO_CONFIG`에 서비스명을 미리 정의할 수 있습니다:

```python
REPO_CONFIG = {
    "your-repo-name": {
        "service_name": "서비스 이름",  # Confluence 검색에 사용
    }
}
```

설정하지 않으면 레포지토리 이름을 서비스명으로 사용하며, Confluence 페이지는 자동으로 검색하거나 대화형으로 선택할 수 있습니다.

## 자동 수집 정보

배포 노트에 자동으로 포함되는 정보:

1. **Git Commit 히스토리**: 이전 태그부터 현재 태그까지의 모든 커밋
2. **변경된 파일 목록**: 추가/수정/삭제된 파일과 변경 라인 수
3. **배포 환경 및 버전**: 태그에서 자동 파싱
4. **배포 일시**: 태그 생성 시간

## CLI 직접 사용 (고급)

Claude 없이 deployment.py를 직접 실행할 수도 있습니다:

```bash
# 대화형 모드 (문서 생성 전 확인)
python deployment.py create --tag dev-v1.2.3
python deployment.py create --tag v2.0.0
python deployment.py create --tag 1.0.1

# 자동 모드 (확인 없이 바로 생성)
python deployment.py create --tag dev-v1.2.3 --no-interactive

# Dry-run (실제 생성하지 않고 미리보기)
python deployment.py create --tag dev-v1.2.3 --dry-run

# 이전 태그 지정
python deployment.py create --tag v1.2.3 --prev-tag v1.2.0
python deployment.py create --tag dev-v1.2.3 --prev-tag dev-v1.2.2
```

## 문제 해결

### Confluence 페이지 생성 실패

1. API 토큰 확인:
   ```bash
   echo $CONFLUENCE_API_TOKEN
   ```

2. Confluence 플러그인 동작 확인:
   ```bash
   python ~/.claude/plugins/cache/sol-plugins/confluence/*/confluence.py search "test"
   ```

3. 대화형 모드 사용:
   - `--no-interactive` 플래그 없이 실행하여 페이지 선택 과정 확인
   - 추천 페이지가 나타나지 않으면 직접 페이지 ID 입력

### 태그 형식

다양한 태그 형식을 지원합니다:
```bash
# 지원되는 형식
dev-v1.2.3      # 환경-버전 형식
v1.2.3          # v 접두사
1.2.3           # 순수 버전
release-1.2.3   # 커스텀 접두사

# 모두 정상적으로 동작합니다
```

### Confluence 페이지 선택

릴리즈 노트를 생성할 Confluence 페이지는:
- 자동으로 관련 페이지를 검색하여 추천합니다
- 추천된 페이지를 선택하거나 직접 페이지 ID를 입력할 수 있습니다
- 새 페이지를 생성할 수도 있습니다

대화형 모드에서 단계별로 안내받을 수 있습니다.

## 확장하기

### 새로운 환경 추가

[deployment.py](deployment.py)의 `ENV_MAPPING`에 환경 추가:

```python
ENV_MAPPING = {
    "dev": "개발",
    "stage": "스테이징",
    "prod": "운영",
    "qa": "QA",  # 새로운 환경
}
```

### 태그 형식 커스터마이징

[deployment.py](deployment.py)의 `parse_tag()` 함수 수정:

```python
def parse_tag(tag: str) -> Optional[Dict[str, str]]:
    # 기본 형식: {환경}-v{버전}
    pattern = r"^(dev|stage|prod)-v(\d+\.\d+\.\d+)$"
    # ...
```

## 기술 스택

- **Python 3.8+**: 메인 로직
- **Git**: 버전 관리 및 태그 생성
- **Confluence API**: 문서 생성/업데이트
- **Claude Code**: 대화형 인터페이스

## 파일 구조

```
smart-tag/
├── .claude-plugin/
│   └── plugin.json          # 플러그인 메타데이터
├── skills/
│   └── tag/
│       ├── SKILL.md         # 스킬 정의
│       └── skill-def.json   # 스킬 메타데이터
├── deployment.py            # 패치노트 생성 CLI
└── README.md               # 이 문서
```

## 라이선스

Internal use only - SOL Team

## 작성자

SOL Team

## 버전 히스토리

- **1.0.5** (2026-02-05)
  - 모든 Git 저장소에서 사용 가능 (레포지토리 제한 제거)
  - 다양한 태그 형식 지원 (환경-버전, 버전만, 커스텀 등)
  - Confluence 페이지 자동 검색 및 추천 기능
  - 명령어 정규화 (`/smart-tag:tag`)

- **1.0.4** (2026-02-05)
  - 릴리즈 노트 기능 개선

- **1.0.0** (2026-02-04)
  - 대화형 태그 생성 기능
  - Confluence 패치노트 자동 생성
  - 버전별 단일 문서 관리
