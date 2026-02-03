# SOL Team Claude Code Plugins

SOL 팀에서 사용하는 Claude Code 플러그인 모음입니다.

## 설치 방법

### 1. 마켓플레이스 추가

```bash
/plugin marketplace add https://gitlab.nexon.com/da_div/SOL/claude-plugins.git
```

또는 SSH:
```bash
/plugin marketplace add git@gitlab.nexon.com:da_div/SOL/claude-plugins.git
```

### 2. 플러그인 설치

```bash
/plugin install confluence@sol-plugins
```

## 환경 설정

### Confluence 플러그인

Confluence API 토큰이 필요합니다:

```bash
export CONFLUENCE_API_TOKEN="your-bearer-token"
```

## 포함된 플러그인

### confluence

Confluence 페이지를 검색, 조회, 생성, 수정하는 플러그인입니다.

**기능:**
- 페이지 검색 (트리 구조로 결과 표시)
- 페이지 조회/생성/수정
- 유해탐지팀 컨플루언스 문서 전용

**사용 예시:**
- "컨플에서 텍스트탐지 API 문서 검색해줘"
- "배포 노트 작성해줘"
- `/confluence:search 텍스트탐지`

## 프로젝트에서 자동 설치 설정

프로젝트의 `.claude/settings.json`에 추가:

```json
{
  "extraKnownMarketplaces": {
    "sol-plugins": {
      "source": {
        "source": "url",
        "url": "https://gitlab.nexon.com/da_div/SOL/claude-plugins.git"
      }
    }
  },
  "enabledPlugins": {
    "confluence@sol-plugins": true
  }
}
```

## GitLab 인증

비공개 저장소 접근을 위해 환경변수 설정:

```bash
export GITLAB_TOKEN=glpat-xxxxxxxxxxxx
```

## 기여하기

새 플러그인을 추가하려면 `plugins/` 폴더에 플러그인을 만들고 `.claude-plugin/marketplace.json`에 등록하세요.
