---
name: auto-patch-notes
description: Git 태그로 패치 노트 자동 생성. "배포 노트", "패치 노트", "릴리즈 노트", "배포 문서 생성" 등의 키워드에서 활성화
---

# 패치 노트 자동 생성 스킬

Git 태그를 기반으로 패치 노트와 릴리즈 노트를 Confluence에 자동으로 생성하는 스킬입니다.

## 트리거

다음 키워드가 포함된 요청에서 활성화됩니다:
- "배포 노트", "패치 노트", "릴리즈 노트"
- "배포 문서 생성", "배포 문서 자동화"
- "deployment", "release", "patch note"

## 환경 설정

**필수 환경변수:**
```bash
export CONFLUENCE_API_TOKEN="your-bearer-token"  # confluence 플러그인과 동일
```

## 지원 레포지토리

현재 다음 레포지토리를 지원합니다:
- **engagement_api_fastapi** (텍스트/이미지탐지 API)
  - 태그 형식: `{환경}-v{버전}` (예: `dev-v1.2.3`, `prod-v2.0.0`)
  - 환경: `dev`, `stage`, `prod`

## 태그 형식

배포 태그는 다음 형식을 따라야 합니다:
```
{환경}-v{버전}
```

예시:
- `dev-v1.0.0` - 개발 환경 버전 1.0.0
- `stage-v1.0.0` - 스테이징 환경 버전 1.0.0
- `prod-v1.0.0` - 운영 환경 버전 1.0.0

## 자동 생성 문서

Git 태그 생성 시 **두 가지 문서**가 자동으로 생성됩니다:

### 1. 간략한 패치노트
- **위치**: "텍스트/이미지 탐지 API 패치노트" 하위
- **내용**: 배포 정보, 주요 변경 사항 요약 (최대 5개 커밋)
- **용도**: 빠른 배포 정보 확인

### 2. 상세 릴리즈 노트
- **위치**: "상세 릴리즈 노트" 페이지 하위 (첫 실행 시 자동 생성)
- **내용**: 전체 커밋 히스토리, 상세 파일 변경 목록, 배포 절차, 롤백 계획
- **용도**: 버전별 자세한 기능 내역 관리

## 자동 수집 정보

배포 노트에 자동으로 포함되는 정보:
1. **Git Commit 히스토리**: 이전 태그부터 현재 태그까지의 모든 커밋
2. **변경된 파일 목록**: 추가/수정/삭제된 파일들의 목록과 변경 라인 수
3. **배포 환경 및 버전**: 태그에서 파싱한 환경과 버전 정보
4. **배포 일시**: 태그 생성 시간

## 대화형 모드

수동 실행 시 사용자와 상호작용합니다:
1. 상세 릴리즈 노트 페이지 위치 확인 (없으면 생성 제안)
2. 생성될 문서 미리보기
3. 생성 전 최종 확인

## Git Hook 설정

자동 배포 노트 생성을 위한 Git hook 설정:

### 1. Hook 설치
```bash
# engagement_api_fastapi 레포에서 실행
cd /path/to/engagement_api_fastapi
cp ${CLAUDE_PLUGIN_ROOT}/hooks/post-tag .git/hooks/
chmod +x .git/hooks/post-tag
```

### 2. Hook 동작 방식
- Git 태그 생성 시 자동으로 실행됩니다
- 태그 형식이 `{환경}-v{버전}`인 경우에만 동작합니다
- Claude Code CLI를 호출하여 배포 노트를 생성합니다

## CLI 사용 방법

수동으로 배포 노트를 생성할 수도 있습니다:

```bash
# 대화형 모드 (기본) - 위치 확인 및 미리보기
python ${CLAUDE_PLUGIN_ROOT}/deployment.py create

# 특정 태그로 생성
python ${CLAUDE_PLUGIN_ROOT}/deployment.py create --tag dev-v1.2.3

# 자동 생성 (비대화형 모드) - Git Hook에서 사용
python ${CLAUDE_PLUGIN_ROOT}/deployment.py create --tag dev-v1.2.3 --no-interactive

# 이전 태그와 비교하여 생성
python ${CLAUDE_PLUGIN_ROOT}/deployment.py create --tag dev-v1.2.3 --prev-tag dev-v1.2.2

# Dry-run (실제 생성하지 않고 미리보기)
python ${CLAUDE_PLUGIN_ROOT}/deployment.py create --tag dev-v1.2.3 --dry-run
```

## 문서 생성 위치

Confluence 문서는 다음 위치에 생성됩니다:

### 간략한 패치노트
- **페이지 ID**: `1719919196`
- **위치**: 유해탐지팀 > 02. 유해탐지팀_업무 > 텍스트/이미지 탐지 > 3. 텍스트/이미지 탐지 API > **텍스트/이미지 탐지 API 패치노트**

### 상세 릴리즈 노트
- **페이지**: "텍스트/이미지탐지 API 상세 릴리즈 노트" (첫 실행 시 자동 생성)
- **위치**: 패치노트 페이지와 같은 레벨

문서 구조:
```
3. 텍스트/이미지 탐지 API
├── 텍스트/이미지 탐지 API 패치노트
│   ├── (2026/02/04) v1.2.3 새로운 필터링 알고리즘 추가
│   │   └── 배포 이력: dev(02/04), stage(02/05), prod(02/10)
│   └── ...
└── 텍스트/이미지탐지 API 상세 릴리즈 노트
    ├── v1.2.3 릴리즈 노트
    │   └── 배포 이력: dev(02/04), stage(02/05), prod(02/10)
    └── ...
```

## 배포 노트 문서 구조

### 버전별 단일 문서
같은 버전은 환경에 관계없이 **하나의 문서**로 관리됩니다.

### 간략한 패치노트
**제목 형식**: `(YYYY/MM/DD) v{버전} {커밋 요약}`

빠른 확인을 위한 요약 정보:
- **배포 이력** (테이블): 환경별 배포 일시
  - 예: dev(02/04), stage(02/05), prod(02/10)
- 주요 변경 사항 (최대 5개 커밋 요약)
- 상세 릴리즈 노트 링크

**동작**:
- 첫 배포: 새 문서 생성
- 같은 버전 다른 환경 배포: 배포 이력 테이블에 환경 추가

### 상세 릴리즈 노트
**제목 형식**: `v{버전} 릴리즈 노트`

자세한 변경 내역:

#### 1. 배포 이력
- 환경별 배포 일시 (테이블 형식)

#### 2. 버전 정보
- 서비스명, 버전

#### 3. 변경 사항
- **전체 Commit 히스토리**: 커밋 메시지, 작성자, 시간
- **변경된 파일 목록**: 추가/수정/삭제된 파일과 라인 수

#### 4. 배포 절차
- 배포 전 체크리스트
- 배포 명령어
- 배포 후 검증 사항

#### 5. 롤백 계획
- 롤백 시나리오
- 롤백 명령어

**동작**:
- 첫 배포: 새 문서 생성
- 같은 버전 다른 환경 배포: 배포 이력 테이블에 환경 추가

## 예시

### 첫 번째 배포 (dev 환경)
```bash
cd /path/to/engagement_api_fastapi
git tag dev-v1.2.3
git push origin dev-v1.2.3

# Hook 자동 실행 → 두 문서 생성:
# 1. "(2026/02/04) v1.2.3 새로운 필터링 알고리즘 추가" - 패치노트
# 2. "v1.2.3 릴리즈 노트" - 상세 릴리즈 노트
```

### 같은 버전을 다른 환경에 배포
```bash
# Stage 환경
git tag stage-v1.2.3
git push origin stage-v1.2.3

# Hook 자동 실행 → 기존 문서 업데이트:
# - 배포 이력: dev(02/04), stage(02/05) 추가

# Prod 환경
git tag prod-v1.2.3
git push origin prod-v1.2.3

# 배포 이력: dev(02/04), stage(02/05), prod(02/10)
```

### 수동 실행
```bash
# Claude Code에서 실행
/auto-patch-notes create dev-v1.2.3
```

## 참조 문서

- `references/hook-guide.md` - Git Hook 설정 가이드
- `templates/deployment-template.md` - 배포 노트 템플릿
