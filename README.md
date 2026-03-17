# SOL Team AI Agent Plugins (Claude Code & Gemini CLI)

SOL 팀에서 사용하는 AI Agent (Claude Code, Gemini CLI) 플러그인 모음입니다.

## 🚀 Gemini CLI 설치 방법

Gemini CLI에서는 이 레포지토리를 로컬에 클론한 뒤, 내부의 스킬 폴더들을 직접 설치하는 방식으로 사용합니다.

### 1. 레포지토리 클론
```bash
git clone https://gitlab.nexon.com/da_div/SOL/claude-plugins.git ~/workspace/claude-plugins
```

### 2. 전체 스킬 설치하기

**옵션 A: 한 번에 설치 (One-liner)**
클론 받은 폴더로 이동한 후 아래 명령어를 실행하면 모든 플러그인이 `user` 스코프(전역)로 일괄 설치됩니다.
```bash
cd ~/workspace/claude-plugins && for d in plugins/*/; do gemini skills install "$d" --scope user; done
```

**옵션 B: 개별 설치 (한 줄씩)**
원하는 스킬만 선택해서 설치하거나 일괄 명령어가 동작하지 않는 환경이라면, 클론 받은 폴더 내에서 아래 명령어를 하나씩 실행하세요.
```bash
cd ~/workspace/claude-plugins
gemini skills install ./plugins/claude-d3js-skill --scope user
gemini skills install ./plugins/code-review --scope user
gemini skills install ./plugins/confluence --scope user
gemini skills install ./plugins/detection-log --scope user
gemini skills install ./plugins/service-lookup --scope user
```

*(설치 후 Gemini CLI 내에서 `/skills reload` 명령어를 입력하면 즉시 적용됩니다.)*

---

## 🤖 Claude Code 설치 방법

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

또는 `/plugin` 명령어로 플러그인 목록을 탐색하여 설치할 수도 있습니다.

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
/plugin install <플러그인명>@sol-plugins
```

또는 `/plugin` 명령어로 플러그인 목록을 탐색하여 설치할 수도 있습니다.

---

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

## 기여하기

새 플러그인을 추가하려면 `plugins/` 폴더에 플러그인을 만들고 `.claude-plugin/marketplace.json`에 등록하세요.
