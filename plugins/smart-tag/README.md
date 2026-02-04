# Smart Tag Plugin

대화형으로 Git 태그를 생성하고, Confluence 패치 노트를 자동으로 작성하는 Claude Code 플러그인입니다.

## 특징

- 🎯 **대화형 워크플로우**: 커밋 선택부터 태그 생성까지 Claude와 대화하며 진행
- 📝 **자동 문서 생성**: 태그 생성과 동시에 Confluence 패치노트 자동 작성
- 📊 **두 가지 문서**: 간략한 패치노트 + 상세 릴리즈 노트
- 🔄 **버전별 관리**: 같은 버전은 하나의 문서로 관리, 환경별 배포 이력 추적
- ⚡ **간단한 사용**: `/tag` 명령 하나로 모든 작업 완료

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
사용자: /tag

Claude: 최근 10개 커밋을 보여드릴게요
        [커밋 목록 표시]

        어느 커밋에 태그를 달까요?

사용자: 맨 위 커밋

Claude: 배포 환경을 선택하세요
        1. dev (개발)
        2. stage (스테이징)
        3. prod (운영)

사용자: dev

Claude: 버전을 입력하세요 (예: 1.2.3)

사용자: 1.2.3

Claude: dev-v1.2.3 태그를 생성하고 패치노트를 작성하시겠어요?

사용자: 네

Claude: ✓ 태그 생성 완료: dev-v1.2.3
        ✓ 패치노트 생성 중...
        ✓ 완료!

        📄 패치노트: https://confluence.../1234567
        📄 릴리즈 노트: https://confluence.../1234568
```

### 빠른 사용 (태그 지정)

```
사용자: /tag dev-v1.2.3

Claude: HEAD 커밋에 dev-v1.2.3 태그를 생성하시겠어요?

사용자: 네

Claude: [태그 생성 + 문서 자동 생성]
```

## 워크플로우

```
1. 사용자: /tag 입력
   ↓
2. Claude: 최근 커밋 목록 표시
   ↓
3. Claude: 대화형 질문
   - 어느 커밋에 태그?
   - 환경은? (dev/stage/prod)
   - 버전은? (예: 1.2.3)
   ↓
4. Claude: git tag 생성
   형식: {환경}-v{버전}
   ↓
5. Claude: deployment.py 자동 실행
   - 패치노트 생성
   - 릴리즈 노트 생성
   ↓
6. Claude: Confluence URL 출력
```

## 태그 형식

```
{환경}-v{버전}
```

**환경**:
- `dev` - 개발 환경
- `stage` - 스테이징 환경
- `prod` - 운영 환경

**버전**: Semantic Versioning (MAJOR.MINOR.PATCH)

**예시**:
- `dev-v1.0.0`
- `stage-v1.2.3`
- `prod-v2.0.0`

## 생성되는 문서

태그 생성 시 **두 가지 문서**가 Confluence에 자동으로 생성됩니다.

### 1. 간략한 패치노트

**위치**: "텍스트/이미지 탐지 API 패치노트" 하위
**제목**: `(YYYY/MM/DD) v{버전} {커밋 요약}`
**예시**: `(2026/02/04) v1.2.3 새로운 필터링 알고리즘 추가`

**포함 내용**:
- 배포 이력 테이블 (환경별 배포 일시)
- 주요 변경 사항 (최대 5개 커밋)
- 상세 릴리즈 노트 링크

### 2. 상세 릴리즈 노트

**위치**: "텍스트/이미지탐지 API 상세 릴리즈 노트" 하위
**제목**: `v{버전} 릴리즈 노트`
**예시**: `v1.2.3 릴리즈 노트`

**포함 내용**:
- 배포 이력 테이블
- 버전 정보
- 전체 커밋 히스토리
- 변경된 파일 목록 (추가/수정/삭제)
- 배포 절차 및 체크리스트
- 롤백 계획

## 버전별 단일 문서 관리

같은 버전은 환경에 관계없이 **하나의 문서**로 관리됩니다.

### 예시: v1.2.3 배포 과정

```
1. dev 환경 배포
   $ /tag dev-v1.2.3
   → 새 문서 생성

2. stage 환경 배포
   $ /tag stage-v1.2.3
   → 기존 문서에 배포 이력 추가

3. prod 환경 배포
   $ /tag prod-v1.2.3
   → 기존 문서에 배포 이력 추가
```

### 최종 배포 이력 테이블

| 환경 | 배포 일시 |
|------|-----------|
| 개발 (dev) | 2026-02-04 10:00 |
| 스테이징 (stage) | 2026-02-05 14:00 |
| 운영 (prod) | 2026-02-10 09:00 |

## Confluence 문서 구조

```
플랫폼 본부 (NAD)
└── 유해탐지팀 컨플 문서
    └── 02. 유해탐지팀_업무
        └── 텍스트/이미지 탐지
            └── 3. 텍스트/이미지 탐지 API
                ├── 텍스트/이미지 탐지 API 패치노트
                │   ├── (2026/02/04) v1.2.3 새로운 기능 추가
                │   ├── (2026/02/01) v1.2.0 성능 개선
                │   └── ...
                └── 텍스트/이미지탐지 API 상세 릴리즈 노트
                    ├── v1.2.3 릴리즈 노트
                    ├── v1.2.0 릴리즈 노트
                    └── ...
```

## 지원 레포지토리

현재 다음 레포지토리를 지원합니다:

### engagement_api_fastapi (텍스트/이미지탐지 API)
- **서비스명**: 텍스트/이미지탐지 API
- **패치노트 페이지 ID**: 1719919196
- **태그 형식**: `{env}-v{version}`

새로운 레포지토리를 추가하려면 [deployment.py](deployment.py)의 `REPO_CONFIG`를 수정하세요.

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

# 자동 모드 (확인 없이 바로 생성)
python deployment.py create --tag dev-v1.2.3 --no-interactive

# Dry-run (실제 생성하지 않고 미리보기)
python deployment.py create --tag dev-v1.2.3 --dry-run

# 이전 태그 지정
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

3. 페이지 ID 확인:
   - [deployment.py](deployment.py)의 `REPO_CONFIG`에서 `patch_notes_page_id` 확인
   - Confluence에서 해당 페이지 존재 여부 확인

### 태그 형식 오류

태그가 `{환경}-v{버전}` 형식인지 확인:
```bash
# 올바른 형식
dev-v1.2.3
stage-v2.0.0
prod-v1.0.1

# 잘못된 형식
v1.2.3        # 환경 누락
dev-1.2.3     # v 누락
dev-v1.2      # 버전 형식 오류
```

### 레포지토리 미지원

현재 레포지토리가 지원되지 않으면:

1. [deployment.py](deployment.py) 열기
2. `REPO_CONFIG`에 새 레포지토리 추가:
   ```python
   REPO_CONFIG = {
       "your-repo-name": {
           "service_name": "서비스 이름",
           "patch_notes_page_id": "Confluence 페이지 ID",
           "release_notes_page_id": None,  # 자동 생성
       }
   }
   ```

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

- **1.0.0** (2026-02-04)
  - 대화형 태그 생성 기능
  - Confluence 패치노트 자동 생성
  - 버전별 단일 문서 관리
