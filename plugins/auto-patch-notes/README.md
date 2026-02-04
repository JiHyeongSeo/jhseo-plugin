# Auto Patch Notes Plugin

Git 태그를 달면 자동으로 패치 노트를 Confluence에 생성하는 Claude Code 플러그인입니다.

## 기능

- Git 태그 생성 시 자동으로 **두 가지 문서**를 Confluence에 생성
  1. **간략한 패치노트**: 빠른 배포 정보 확인용
  2. **상세 릴리즈 노트**: 버전별 자세한 기능 내역
- 커밋 히스토리 및 파일 변경 목록 자동 수집
- 사용자 대화형 모드: 문서 생성 전 위치 확인 및 미리보기
- 배포 절차 및 롤백 계획 템플릿 제공
- `{환경}-v{버전}` 형식의 태그 지원 (예: `dev-v1.2.3`, `prod-v2.0.0`)

## 사전 요구사항

- Python 3.8 이상
- Git
- Confluence API Token
- [confluence 플러그인](../confluence) 설치 필요

## 설치

### 1. 환경 변수 설정

```bash
export CONFLUENCE_API_TOKEN="your-bearer-token"
```

### 2. Git Hook 설치 (자동 생성을 원하는 경우)

배포 대상 레포지토리에서 다음 명령어를 실행합니다:

```bash
# engagement_api_fastapi 레포에서 실행
cd /path/to/engagement_api_fastapi

# Hook 복사
cp /path/to/claude-plugins/plugins/auto-patch-notes/hooks/post-tag .git/hooks/

# 실행 권한 부여
chmod +x .git/hooks/post-tag
```

### 3. 레포지토리 설정

`deployment.py`의 `REPO_CONFIG`는 이미 설정되어 있습니다:

```python
REPO_CONFIG = {
    "engagement_api_fastapi": {
        "service_name": "텍스트/이미지탐지 API",
        "patch_notes_page_id": "1719919196",  # 패치노트 페이지
        "release_notes_page_id": None,  # 자동 생성 또는 검색
    }
}
```

**참고:**
- `patch_notes_page_id`: 간략한 패치노트가 생성될 페이지 (이미 설정됨)
- `release_notes_page_id`: 상세 릴리즈 노트가 생성될 페이지 (첫 실행 시 자동으로 생성되거나 검색)

## 사용 방법

### 자동 생성 (Git Hook 사용)

Git 태그를 생성하면 자동으로 배포 노트가 생성됩니다:

```bash
# 태그 생성
git tag dev-v1.2.3

# 원격 저장소에 푸시 (hook은 로컬 태그 생성 시 실행됨)
git push origin dev-v1.2.3
```

### 수동 생성

#### 기본 사용 (대화형 모드)
```bash
# 최신 태그로 생성
python deployment.py create

# 특정 태그로 생성
python deployment.py create --tag dev-v1.2.3
```

**대화형 모드에서는:**
1. 상세 릴리즈 노트 페이지 위치 확인 (없으면 생성 제안)
2. 생성될 문서 미리보기
3. 생성 전 최종 확인

#### 자동 생성 (비대화형 모드)
```bash
# Git Hook에서 사용하기 좋음
python deployment.py create --tag dev-v1.2.3 --no-interactive
```

#### 이전 태그 지정
```bash
python deployment.py create --tag dev-v1.2.3 --prev-tag dev-v1.2.2
```

#### Dry-run (미리보기만)
```bash
python deployment.py create --tag dev-v1.2.3 --dry-run
```

### Claude Code에서 사용

```
/auto-patch-notes create dev-v1.2.3
```

## 태그 형식

배포 태그는 다음 형식을 따라야 합니다:

```
{환경}-v{버전}
```

지원하는 환경:
- `dev`: 개발 환경
- `stage`: 스테이징 환경
- `prod`: 운영 환경

버전 형식: `MAJOR.MINOR.PATCH` (Semantic Versioning)

예시:
- `dev-v1.0.0`
- `stage-v1.2.3`
- `prod-v2.0.0`

## 생성되는 문서 구조

### 버전별 단일 문서 구조

같은 버전은 환경에 관계없이 **하나의 문서**로 관리됩니다.

#### 1. 간략한 패치노트 (빠른 확인용)
**위치**: "텍스트/이미지 탐지 API 패치노트" 하위
**제목**: `(YYYY/MM/DD) v{버전} {커밋 요약}`
**예**: `(2026/02/04) v1.2.3 새로운 필터링 알고리즘 추가`

**포함 내용**:
- **배포 이력**: 환경별 배포 일시 (테이블 형식)
  - dev: 2026/02/04
  - stage: 2026/02/05
  - prod: 2026/02/10
- 주요 변경 사항 요약 (최대 5개 커밋)
- 상세 릴리즈 노트 링크

**동작 방식**:
- 첫 배포 시: 새 문서 생성
- 같은 버전 다른 환경 배포 시: 배포 이력 테이블에 환경 추가

#### 2. 상세 릴리즈 노트 (자세한 내역)
**위치**: "텍스트/이미지탐지 API 상세 릴리즈 노트" 하위
**제목**: `v{버전} 릴리즈 노트`
**예**: `v1.2.3 릴리즈 노트`

**포함 내용**:
- **배포 이력**: 환경별 배포 일시 (테이블 형식)
- **버전 정보**: 서비스명, 버전
- **변경 사항**:
  - 전체 Commit 히스토리 (Hash, 작성자, 날짜, 메시지)
  - 변경된 파일 목록 (추가/수정/삭제, 라인 수 포함)
- **배포 절차**:
  - 배포 전 체크리스트
  - 배포 명령어
  - 배포 후 검증 항목
- **롤백 계획**:
  - 롤백 시나리오
  - 롤백 명령어

**동작 방식**:
- 첫 배포 시: 새 문서 생성
- 같은 버전 다른 환경 배포 시: 배포 이력 테이블에 환경 추가

## Confluence 문서 위치

문서는 다음 구조로 생성됩니다:

```
플랫폼 본부 (NAD)
└── 유해탐지팀 컨플 문서
    └── 02. 유해탐지팀_업무
        └── 텍스트/이미지 탐지
            └── 3. 텍스트/이미지 탐지 API
                ├── 텍스트/이미지 탐지 API 패치노트
                │   ├── (2026/02/04) v1.2.3 새로운 필터링 알고리즘 추가 ⭐
                │   │   └── 배포 이력: dev(02/04), stage(02/05), prod(02/10)
                │   ├── (2026/02/01) v1.2.0 성능 개선
                │   └── ...
                └── 텍스트/이미지탐지 API 상세 릴리즈 노트 🆕
                    ├── v1.2.3 릴리즈 노트 ⭐
                    │   └── 배포 이력: dev(02/04), stage(02/05), prod(02/10)
                    ├── v1.2.0 릴리즈 노트
                    └── ...
```

**문서 제목 형식**:
- 패치노트: `(YYYY/MM/DD) v{버전} {커밋 요약}`
- 릴리즈 노트: `v{버전} 릴리즈 노트`

**중요**: 같은 버전은 환경에 관계없이 하나의 문서로 관리되며, 배포 이력 테이블에 환경별 배포 일시가 기록됩니다.

## 사용 예시

### 첫 번째 배포 (dev 환경)
```bash
cd /path/to/engagement_api_fastapi

# 개발 완료 후 태그 생성
git tag dev-v1.2.3
git push origin dev-v1.2.3

# Hook이 자동으로 실행되어 두 문서 생성:
# 1. "(2026/02/04) v1.2.3 새로운 필터링 알고리즘 추가" - 패치노트
# 2. "v1.2.3 릴리즈 노트" - 상세 릴리즈 노트
```

### 같은 버전을 다른 환경에 배포
```bash
# Stage 환경에 배포
git tag stage-v1.2.3
git push origin stage-v1.2.3

# Hook이 자동으로 실행되어 기존 문서 업데이트:
# - 패치노트: 배포 이력에 stage(02/05) 추가
# - 릴리즈 노트: 배포 이력에 stage(02/05) 추가

# Prod 환경에 배포
git tag prod-v1.2.3
git push origin prod-v1.2.3

# 최종 배포 이력: dev(02/04), stage(02/05), prod(02/10)
```

### 결과 확인

Confluence에서 다음 문서를 확인할 수 있습니다:

**패치노트**:
- 제목: `(2026/02/04) v1.2.3 새로운 필터링 알고리즘 추가`
- 배포 이력 테이블:
  | 환경 | 배포 일시 |
  |------|-----------|
  | 개발 (dev) | 2026-02-04 |
  | 스테이징 (stage) | 2026-02-05 |
  | 운영 (prod) | 2026-02-10 |

**상세 릴리즈 노트**:
- 제목: `v1.2.3 릴리즈 노트`
- 동일한 배포 이력 + 전체 커밋 히스토리 + 파일 변경 목록

## 문제 해결

### Hook이 실행되지 않는 경우

1. Hook 파일 실행 권한 확인:
   ```bash
   ls -l .git/hooks/post-tag
   # -rwxr-xr-x 여야 함
   ```

2. Hook 파일 경로 확인:
   ```bash
   head -1 .git/hooks/post-tag
   # #!/bin/bash 여야 함
   ```

3. 플러그인 경로 확인:
   ```bash
   cd /path/to/repo
   .git/hooks/post-tag
   ```

### Confluence 페이지 생성 실패

1. API 토큰 확인:
   ```bash
   echo $CONFLUENCE_API_TOKEN
   ```

2. confluence 플러그인 동작 확인:
   ```bash
   python /path/to/confluence.py search "test"
   ```

3. 상위 페이지 ID 확인:
   - `deployment.py`의 `REPO_CONFIG`에서 `parent_page_id` 확인
   - Confluence에서 해당 페이지 존재 여부 확인

### 태그 형식 오류

태그가 `{환경}-v{버전}` 형식인지 확인:
```bash
git tag -l | grep -E "^(dev|stage|prod)-v[0-9]+\.[0-9]+\.[0-9]+$"
```

## 확장하기

### 새로운 레포지토리 추가

1. `deployment.py`의 `REPO_CONFIG`에 레포지토리 추가:
   ```python
   REPO_CONFIG = {
       "your-repo-name": {
           "service_name": "서비스 이름",
           "parent_page_id": "Confluence 상위 페이지 ID",
       }
   }
   ```

2. 레포지토리에 Git Hook 설치

### 새로운 환경 추가

1. `deployment.py`의 `ENV_MAPPING`에 환경 추가:
   ```python
   ENV_MAPPING = {
       "dev": "개발",
       "stage": "스테이징",
       "prod": "운영",
       "qa": "QA",  # 새로운 환경 추가
   }
   ```

2. `hooks/post-tag`의 정규식 패턴 수정:
   ```bash
   if ! echo "$TAG" | grep -qE "^(dev|stage|prod|qa)-v[0-9]+\.[0-9]+\.[0-9]+$"; then
   ```

## 라이선스

Internal use only - SOL Team

## 작성자

SOL Team
