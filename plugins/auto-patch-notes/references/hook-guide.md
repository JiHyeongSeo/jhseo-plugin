# Git Hook 설정 가이드

이 문서는 배포 노트 자동 생성을 위한 Git Hook 설정 방법을 설명합니다.

## Git Hook이란?

Git Hook은 Git 작업 시 특정 시점에 자동으로 실행되는 스크립트입니다. 이 플러그인은 `post-tag` hook을 사용하여 태그 생성 시 자동으로 배포 노트를 생성합니다.

## 지원하는 Hook

### post-tag

태그가 생성된 후 자동으로 실행됩니다.

**트리거 조건:**
- Git 태그 생성 시 (`git tag {태그명}`)
- 태그 형식이 `{환경}-v{버전}` 패턴과 일치할 때

**동작:**
1. 생성된 태그 확인
2. 태그 형식 검증 (예: `dev-v1.2.3`)
3. `deployment.py` 스크립트 실행
4. Confluence 배포 노트 자동 생성

## 설치 방법

### 1. 대상 레포지토리 확인

현재 `engagement_api_fastapi` 레포지토리만 지원됩니다. 다른 레포지토리를 추가하려면 `deployment.py`의 `REPO_CONFIG`를 수정해야 합니다.

### 2. Hook 파일 복사

```bash
# engagement_api_fastapi 레포지토리로 이동
cd /path/to/engagement_api_fastapi

# Hook 파일 복사
cp /path/to/claude-plugins/plugins/deployment-notes/hooks/post-tag .git/hooks/

# 실행 권한 부여
chmod +x .git/hooks/post-tag
```

### 3. Hook 동작 확인

테스트 태그를 생성하여 Hook이 제대로 동작하는지 확인합니다:

```bash
# 테스트 태그 생성 (dry-run)
git tag dev-v0.0.1-test

# Hook 수동 실행 (테스트)
.git/hooks/post-tag

# 테스트 태그 삭제
git tag -d dev-v0.0.1-test
```

## Hook 커스터마이징

### 태그 형식 변경

기본적으로 `{환경}-v{버전}` 형식만 지원합니다. 다른 형식을 사용하려면:

1. **post-tag 스크립트 수정:**
   ```bash
   # 기존 패턴
   if ! echo "$TAG" | grep -qE "^(dev|stage|prod)-v[0-9]+\.[0-9]+\.[0-9]+$"; then

   # 새 패턴 (예: release/v{버전})
   if ! echo "$TAG" | grep -qE "^release/v[0-9]+\.[0-9]+\.[0-9]+$"; then
   ```

2. **deployment.py의 parse_tag() 함수 수정:**
   ```python
   def parse_tag(tag: str) -> Optional[Dict[str, str]]:
       # 새로운 패턴에 맞게 수정
       pattern = r"^release/v(\d+\.\d+\.\d+)$"
       match = re.match(pattern, tag)
       if not match:
           return None
       return {"env": "prod", "version": match.group(1)}
   ```

### 알림 추가

Hook 실행 시 Slack 등으로 알림을 보내려면:

```bash
# post-tag 파일에 추가
if [ $? -eq 0 ]; then
    echo "✓ Deployment note created successfully"

    # Slack 알림 (예시)
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"배포 노트 생성 완료: $TAG\"}" \
        YOUR_SLACK_WEBHOOK_URL
else
    echo "✗ Failed to create deployment note"
fi
```

## 문제 해결

### Hook이 실행되지 않음

**원인 1: 실행 권한 없음**
```bash
# 확인
ls -l .git/hooks/post-tag

# 해결
chmod +x .git/hooks/post-tag
```

**원인 2: 태그 형식 불일치**
```bash
# 확인
echo "dev-v1.2.3" | grep -qE "^(dev|stage|prod)-v[0-9]+\.[0-9]+\.[0-9]+$"
echo $?  # 0이면 일치, 1이면 불일치

# 해결: 올바른 형식으로 태그 생성
git tag dev-v1.2.3  # 올바름
git tag v1.2.3      # 틀림 (환경 없음)
git tag dev-1.2.3   # 틀림 (v 접두사 없음)
```

**원인 3: 플러그인 경로 오류**
```bash
# Hook 스크립트에서 경로 확인
cat .git/hooks/post-tag | grep DEPLOYMENT_SCRIPT

# 경로가 잘못되었다면 수동으로 수정
vi .git/hooks/post-tag
```

### Hook이 실행되지만 문서 생성 실패

**원인 1: Confluence API Token 없음**
```bash
# 확인
echo $CONFLUENCE_API_TOKEN

# 해결
export CONFLUENCE_API_TOKEN="your-token"
```

**원인 2: 레포지토리 설정 없음**
```bash
# deployment.py의 REPO_CONFIG 확인
python3 /path/to/deployment.py create --tag dev-v1.2.3

# 에러 메시지 확인
# "Unsupported repository: xxx" 라면 REPO_CONFIG에 레포 추가 필요
```

**원인 3: Confluence 페이지 권한 없음**
```bash
# confluence 플러그인으로 권한 확인
python3 /path/to/confluence.py get YOUR_PARENT_PAGE_ID
```

### Hook 실행 로그 확인

Hook 실행 로그를 남기려면:

```bash
# post-tag 파일 수정
#!/bin/bash
# 로그 파일 경로
LOG_FILE="/tmp/post-tag-$(date +%Y%m%d).log"

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 기존 코드 전에 로그 추가
log "=== Post-tag hook started ==="
log "Tag: $TAG"

# ... 기존 코드 ...

log "=== Post-tag hook finished ==="
```

## 고급 설정

### 여러 레포지토리에서 공유

여러 레포지토리에서 동일한 Hook을 사용하려면:

1. **공유 Hook 디렉토리 생성:**
   ```bash
   mkdir -p ~/.git-templates/hooks
   cp /path/to/post-tag ~/.git-templates/hooks/
   chmod +x ~/.git-templates/hooks/post-tag
   ```

2. **Git 템플릿 설정:**
   ```bash
   git config --global init.templateDir ~/.git-templates
   ```

3. **기존 레포지토리에 적용:**
   ```bash
   cd /path/to/repo
   git init  # Hook이 자동으로 복사됨
   ```

### 조건부 실행

특정 브랜치에서만 Hook을 실행하려면:

```bash
# post-tag 파일에 추가
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
    echo "Hook only runs on main/master branch"
    exit 0
fi
```

### 비동기 실행

배포 노트 생성이 오래 걸리는 경우 백그라운드로 실행:

```bash
# post-tag 파일 수정
echo "Generating deployment note in background..."
python3 "$DEPLOYMENT_SCRIPT" create --tag "$TAG" > /tmp/deployment-$TAG.log 2>&1 &
echo "Check log: /tmp/deployment-$TAG.log"
```

## 참고 자료

- [Git Hooks 공식 문서](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/)
- [Semantic Versioning](https://semver.org/)

## 추가 Hook

필요에 따라 다른 Hook도 추가할 수 있습니다:

### pre-push (푸시 전 검증)

```bash
#!/bin/bash
# .git/hooks/pre-push

# 태그 형식 검증
for tag in $(git tag --points-at HEAD); do
    if ! echo "$tag" | grep -qE "^(dev|stage|prod)-v[0-9]+\.[0-9]+\.[0-9]+$"; then
        echo "Error: Invalid tag format: $tag"
        echo "Expected: {env}-v{version}"
        exit 1
    fi
done
```

### post-checkout (체크아웃 후 알림)

```bash
#!/bin/bash
# .git/hooks/post-checkout

TAG=$(git describe --tags --exact-match 2>/dev/null)
if [ -n "$TAG" ]; then
    echo "Checked out deployment tag: $TAG"
    echo "Run 'python deployment.py create --tag $TAG' to create deployment note"
fi
```
