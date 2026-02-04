# 배포 노트 플러그인 사용 예시

실제 사용 시나리오와 예시를 제공합니다.

## 시나리오 1: 개발 환경 배포

### 상황
`engagement_api_fastapi` 레포에서 새로운 기능을 개발하고 개발 환경에 배포합니다.

### 단계

1. **개발 완료 및 커밋**
   ```bash
   cd /path/to/engagement_api_fastapi
   git add .
   git commit -m "feat: 새로운 텍스트 필터링 알고리즘 추가"
   ```

2. **태그 생성**
   ```bash
   # 개발 환경 배포를 위한 태그 생성
   git tag dev-v1.3.0
   ```

3. **자동 배포 노트 생성**
   태그 생성 시 post-tag hook이 자동으로 실행되어:
   - 이전 dev 태그 (`dev-v1.2.9`)부터 현재까지의 커밋 수집
   - 변경된 파일 목록 수집
   - Confluence에 배포 노트 자동 생성

4. **원격 저장소에 푸시**
   ```bash
   git push origin dev-v1.3.0
   ```

### 생성된 문서

**Confluence 위치:**
```
NAD 공간
└── 유해탐지팀 컨플 문서
    └── 텍스트/이미지탐지 API
        └── 배포 이력
            └── (2026/02/04) dev-v1.3.0 배포
```

**문서 내용:**
- 배포 정보: 개발 환경, v1.3.0, 2026-02-04
- 변경 사항: 5개 커밋, 12개 파일 변경
- 배포 절차 및 롤백 계획

## 시나리오 2: 스테이징 환경 배포

### 상황
개발 환경에서 테스트가 완료되어 스테이징 환경으로 배포합니다.

### 단계

1. **메인 브랜치로 머지**
   ```bash
   git checkout main
   git merge develop
   ```

2. **스테이징 태그 생성**
   ```bash
   git tag stage-v1.3.0
   git push origin stage-v1.3.0
   ```

3. **배포 노트 자동 생성**
   이전 스테이징 태그 (`stage-v1.2.0`)부터의 변경 사항이 문서화됩니다.

### 특이사항
- stage 환경은 이전 stage 태그와 비교합니다
- dev 태그는 무시됩니다 (환경별로 독립적으로 관리)

## 시나리오 3: 운영 환경 배포

### 상황
스테이징 환경에서 충분히 검증되어 운영 환경에 배포합니다.

### 단계

1. **운영 태그 생성**
   ```bash
   git checkout main
   git tag prod-v1.3.0
   git push origin prod-v1.3.0
   ```

2. **배포 노트 확인**
   자동 생성된 배포 노트를 확인하고 필요 시 수동으로 추가 정보를 기입합니다.

3. **배포 실행**
   배포 노트의 배포 절차를 따라 운영 환경에 배포합니다.

## 시나리오 4: 수동으로 배포 노트 생성

### 상황
Hook이 설치되지 않았거나, 이미 생성된 태그에 대해 배포 노트를 생성해야 합니다.

### CLI 사용

```bash
cd /path/to/engagement_api_fastapi

# 특정 태그로 생성
python /path/to/claude-plugins/plugins/deployment-notes/deployment.py \
    create --tag prod-v1.3.0

# 이전 태그 명시
python /path/to/claude-plugins/plugins/deployment-notes/deployment.py \
    create --tag prod-v1.3.0 --prev-tag prod-v1.2.0

# Dry-run (실제 생성하지 않고 미리보기)
python /path/to/claude-plugins/plugins/deployment-notes/deployment.py \
    create --tag prod-v1.3.0 --dry-run
```

### 출력 예시

```json
{
  "success": true,
  "tag": "prod-v1.3.0",
  "prev_tag": "prod-v1.2.0",
  "commits": 15,
  "file_changes": 23,
  "url": "https://confluence.nexon.com/pages/viewpage.action?pageId=12345678"
}
```

## 시나리오 5: 핫픽스 배포

### 상황
운영 환경에서 긴급 버그가 발견되어 즉시 수정해야 합니다.

### 단계

1. **핫픽스 브랜치 생성**
   ```bash
   git checkout -b hotfix/v1.3.1 prod-v1.3.0
   ```

2. **버그 수정 및 커밋**
   ```bash
   git commit -m "fix: 심각한 메모리 누수 수정"
   ```

3. **핫픽스 태그 생성**
   ```bash
   git tag prod-v1.3.1
   git push origin prod-v1.3.1
   ```

4. **배포 노트 확인**
   자동 생성된 배포 노트에서 변경 사항을 확인합니다.
   - 이전 태그: `prod-v1.3.0`
   - 현재 태그: `prod-v1.3.1`
   - 커밋: 1개 (버그 수정)

5. **메인 브랜치로 백포트**
   ```bash
   git checkout main
   git merge hotfix/v1.3.1
   ```

## 시나리오 6: 배포 노트 수정

### 상황
자동 생성된 배포 노트에 추가 정보를 입력해야 합니다.

### Confluence 플러그인 사용

```bash
# 1. 배포 노트 페이지 검색
python /path/to/confluence.py search "prod-v1.3.0 배포"

# 2. 페이지 ID 확인
# 출력: page_id=12345678

# 3. 현재 내용 확인
python /path/to/confluence.py get 12345678

# 4. 내용 업데이트
python /path/to/confluence.py update 12345678 \
    -c "<h2>추가 정보</h2><p>데이터베이스 마이그레이션 필요</p>..."
```

## 시나리오 7: 여러 환경에 동시 배포

### 상황
동일한 버전을 개발, 스테이징 환경에 동시에 배포합니다.

### 단계

```bash
# 개발 환경
git tag dev-v1.4.0
git push origin dev-v1.4.0

# 스테이징 환경
git tag stage-v1.4.0
git push origin stage-v1.4.0
```

### 결과
각 환경별로 독립적인 배포 노트가 생성됩니다:
- `(2026/02/04) dev-v1.4.0 배포`
- `(2026/02/04) stage-v1.4.0 배포`

## 시나리오 8: 롤백 수행

### 상황
운영 환경 배포 후 심각한 문제가 발견되어 롤백이 필요합니다.

### 단계

1. **배포 노트에서 롤백 정보 확인**
   Confluence에서 현재 배포 노트를 열어 "롤백 계획" 섹션 확인

2. **이전 버전으로 롤백**
   ```bash
   git checkout prod-v1.3.0
   # 배포 스크립트 실행
   ```

3. **롤백 태그 생성 (선택사항)**
   ```bash
   git tag prod-v1.3.0-rollback
   ```

4. **배포 노트 업데이트**
   롤백 사실을 기록:
   ```
   ## 롤백 이력
   - 롤백 일시: 2026-02-04 15:30
   - 롤백 사유: 메모리 누수로 인한 서비스 불안정
   - 롤백 버전: prod-v1.3.0
   ```

## 문제 해결 예시

### 문제 1: Hook이 실행되지 않음

**증상:**
```bash
git tag dev-v1.5.0
# 아무 출력 없음
```

**진단:**
```bash
# Hook 존재 여부 확인
ls -la .git/hooks/post-tag
# ls: cannot access '.git/hooks/post-tag': No such file or directory

# Hook 수동 실행 테스트
.git/hooks/post-tag
```

**해결:**
```bash
# Hook 설치
cp /path/to/claude-plugins/plugins/deployment-notes/hooks/post-tag .git/hooks/
chmod +x .git/hooks/post-tag
```

### 문제 2: Confluence 페이지 생성 실패

**증상:**
```json
{
  "error": "Failed to create page: 401 Unauthorized"
}
```

**진단:**
```bash
# API Token 확인
echo $CONFLUENCE_API_TOKEN
# (empty)

# confluence 플러그인 테스트
python /path/to/confluence.py search "test"
```

**해결:**
```bash
export CONFLUENCE_API_TOKEN="your-token-here"
```

### 문제 3: 태그 형식 오류

**증상:**
```bash
git tag v1.5.0
# Hook이 실행되지만 문서가 생성되지 않음
```

**로그:**
```
Tag format does not match deployment pattern: v1.5.0
Expected format: {env}-v{version}
```

**해결:**
```bash
# 잘못된 태그 삭제
git tag -d v1.5.0

# 올바른 형식으로 재생성
git tag dev-v1.5.0
```

## 고급 사용법

### 커스텀 배포 노트 템플릿

`templates/deployment-template.md`를 수정하여 팀의 배포 프로세스에 맞게 커스터마이즈할 수 있습니다.

### 배포 노트 검색

```bash
# 특정 버전 검색
python /path/to/confluence.py search "v1.3.0 배포"

# 특정 환경 검색
python /path/to/confluence.py search "prod 배포"

# 특정 기간 검색
python /path/to/confluence.py search "2026/02 배포"
```

### 배포 이력 트리 확인

```bash
# Confluence 페이지 구조 확인
python /path/to/confluence.py tree -s NAD
```

## 참고사항

### 버전 관리 전략

- **개발 환경**: 기능 개발마다 버전 증가 (1.0.0 → 1.1.0 → 1.2.0)
- **스테이징 환경**: 개발 검증 후 동일 버전으로 배포
- **운영 환경**: 스테이징 검증 후 동일 버전으로 배포

### 태그 네이밍 규칙

- MAJOR 버전: 하위 호환성이 깨지는 변경
- MINOR 버전: 하위 호환성을 유지하는 기능 추가
- PATCH 버전: 버그 수정

예시:
- `1.0.0` → `2.0.0`: API 스펙 변경 (Breaking Change)
- `1.0.0` → `1.1.0`: 새로운 기능 추가
- `1.0.0` → `1.0.1`: 버그 수정
