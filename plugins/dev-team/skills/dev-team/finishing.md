---
name: finishing-a-development-branch
description: 구현 완료 후 브랜치를 어떻게 처리할지 옵션을 제시하고 실행
---

# Finishing a Development Branch

구현 완료 후 테스트를 검증하고 브랜치 처리 옵션을 제시한다.

## Step 1: 테스트 검증

```bash
# 프로젝트에 맞는 테스트 명령 실행
npm test / pytest / go test ./... / cargo test
```

실패 시 수정 후 재실행. 테스트가 통과해야 다음 단계로 진행.

## Step 2: 베이스 브랜치 확인

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

## Step 3: 옵션 제시

```
구현이 완료되었습니다. 어떻게 하시겠어요?

1. 로컬에서 <base-branch>에 머지
2. Push 후 Pull Request 생성
3. 브랜치 유지 (나중에 처리)
4. 작업 폐기
```

## Step 4: 선택 실행

### 옵션 1: 로컬 머지

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
# 테스트 재실행
git branch -d <feature-branch>
```

### 옵션 2: PR 생성

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<변경 내용 2-3줄>

## Test Plan
- [ ] <검증 단계>
EOF
)"
```

### 옵션 3: 브랜치 유지

현재 브랜치를 그대로 유지. 아무것도 하지 않음.

### 옵션 4: 작업 폐기

**먼저 확인:**
```
다음이 영구 삭제됩니다:
- 브랜치: <name>
- 커밋: <commit-list>

'discard' 를 입력하여 확인하세요.
```

확인 후:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```
