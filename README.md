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
/plugin install <플러그인명>@sol-plugins
```

## 포함된 플러그인

### confluence

Confluence 페이지를 검색, 조회, 생성, 수정하는 플러그인입니다.

**설치:**
```bash
/plugin install confluence@sol-plugins
```

**환경 설정:**
```bash
export CONFLUENCE_API_TOKEN="your-bearer-token"
```

**기능:**
- 페이지 검색 (트리 구조로 결과 표시)
- 페이지 조회/생성/수정
- 유해탐지팀 컨플루언스 문서 전용

**사용 예시:**
- "컨플에서 텍스트탐지 API 문서 검색해줘"
- "배포 노트 작성해줘"
- `/confluence:search 텍스트탐지`

---

## 프로젝트에서 마켓플레이스 자동 등록

프로젝트의 `.claude/settings.json`에 추가하면, 팀원들이 마켓플레이스 URL을 직접 입력하지 않아도 됩니다:

```json
{
  "extraKnownMarketplaces": {
    "sol-plugins": {
      "source": {
        "source": "url",
        "url": "https://gitlab.nexon.com/da_div/SOL/claude-plugins.git"
      }
    }
  }
}
```

이후 플러그인 설치:
```bash
/plugin install confluence@sol-plugins
```

## 기여하기

새 플러그인을 추가하려면 `plugins/` 폴더에 플러그인을 만들고 `.claude-plugin/marketplace.json`에 등록하세요.
