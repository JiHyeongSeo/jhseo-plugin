# SOL Team Claude Code Plugins

이 레포지토리는 SOL 팀 공용 Claude Code 플러그인 소스 코드입니다.

## 플러그인 구조

```
plugins/
├── confluence/     # Confluence 연동 플러그인
└── code-review/    # 코드 리뷰 플러그인 (sol)
```

## 플러그인 추가/수정 가이드

1. `plugins/` 폴더에 플러그인 디렉토리 생성
2. `.claude-plugin/plugin.json` 작성
3. `.claude-plugin/marketplace.json`에 플러그인 등록
4. README.md 업데이트

## Push 후 문서 업데이트 워크플로우

**중요**: 플러그인을 수정하고 push한 후, 아래 절차로 Confluence 문서를 업데이트해주세요.

### 업데이트 방법

Claude에게 다음과 같이 요청:

```
플러그인 업데이트 사항을 "Claude Code 팀 공용 플러그인" 문서에 반영해줘
```

### 문서에 반영할 내용

- 플러그인 버전 변경
- 새 기능 추가/제거
- 사용법 변경
- 설치 방법 변경

### 자동 검색 키워드

"Claude Code 팀 공용 플러그인" 문서를 confluence 플러그인으로 검색하여 업데이트합니다.
