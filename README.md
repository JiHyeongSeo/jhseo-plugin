# jhseo-cursor-backup

개인 **Cursor** 설정 백업·복구용 레포입니다.  
(예전 SOL Team Claude/Gemini 플러그인 모노레포는 정리됨 — `archive/README.md` 참고)

## 무엇을 백업하나

| 경로 (Linux) | 내용 |
|--------------|------|
| `~/.config/Cursor/User/settings.json` | IDE 설정 |
| `~/.config/Cursor/User/keybindings.json` | 단축키 |
| `~/.config/Cursor/User/snippets/` | 스니펫 |
| `~/.cursor/cli-config.json` | Agent CLI 설정 |
| `~/.cursor/mcp.json` | MCP 서버 (있을 때) |
| `~/.cursor/hooks.json`, `hooks/` | 훅 (있을 때) |
| `~/.cursor/rules/` | **전역** User Rules |
| `home/projects/<slug>/.cursor/` | (선택) 프로젝트별 rules/skills |

**백업하지 않음:** `~/.cursor/projects/` (채팅 기록), `skills-cursor/` (Cursor 내장), extensions, 캐시.

## 빠른 사용

```bash
cd ~/jhseo-plugin

# 이 PC → 레포
./scripts/backup.sh
./scripts/backup.sh ~/stock          # stock 프로젝트 .cursor 도 포함

git add home/ && git commit -m "backup cursor settings"
git push

# 새 PC / 복구
git clone git@github.com:JiHyeongSeo/jhseo-plugin.git
cd jhseo-plugin
./scripts/restore.sh
./scripts/install-skills.sh ~/my-project   # Matt Pocock + Taste + template rules
```

## 스킬 재설치

`skills.manifest.yaml` 에 정의:

- **mattpocock/skills** (전체)
- **taste-skill** (design-taste-frontend, minimalist-ui, redesign-existing-projects)

프로젝트 공통 규칙 템플릿: `templates/rules/` (Karpathy, Ponytail, taste-dashboard)

## 새 프로젝트에 규칙 복사

```bash
mkdir -p ~/myapp/.cursor/rules
cp templates/rules/*.mdc ~/myapp/.cursor/rules/
```

## 주의

- API 키·토큰은 **커밋하지 마세요**. `.env`는 백업 대상 아님.
- `cli-config.json`에 민감 정보가 있으면 `home/.cursor/cli-config.json` 을 검토 후 커밋.
- 복구 후 **Cursor IDE / CLI 재시작** 필요.

## 레거시

Claude Code / Gemini CLI 플러그인은 `git` 히스토리 또는 `legacy/sol-plugins` 브랜치(생성한 경우)에서 복구.
