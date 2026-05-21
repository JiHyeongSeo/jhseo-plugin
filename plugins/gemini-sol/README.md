# gemini-sol

SOL 팀용 Gemini CLI 연동 플러그인. [amurtare/gemini_plugin_for_claude](https://gitlab.nexon.com/amurtare/gemini_plugin_for_claude)에서 **동기 호출 기능만** 추출.

## 왜 fork했나

원본 플러그인은 강력하지만 다음 기능 때문에 우리 워크플로우에 안 맞음:
- `/gemini:task --background` — 백그라운드 작업, 추적 시스템 분리되어 알림 누락 발생
- `gemini:gemini-rescue` 서브에이전트 — 같은 알림 누락 문제
- Review Gate 훅 — Stop 시점에 매번 발동, 무거움

SOL 팀 정책은 **동기 호출만** 사용. 그래서 필요한 것만 추출.

## 제공 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/gemini:ask` | Gemini에게 질문 (read-only, 동기) |
| `/gemini:review` | 코드 리뷰 (동기, foreground 강제) |
| `/gemini:setup` | Gemini CLI 설치/인증 상태 확인 |

## 요구사항

- Node.js 18.18+
- Gemini CLI: `npm install -g @google/gemini-cli`
- 인증 (Google OAuth, `GEMINI_API_KEY`, 또는 Vertex AI)

## 설치 (SOL 마켓플레이스에서)

```
/plugin install gemini-sol@sol-plugins
```

## 사용 예

```
/gemini:ask 이 알고리즘 더 효율적인 방법 있어?
/gemini:review src/auth.py
/gemini:setup
```

## 원본과의 차이

**제거된 것**:
- 백그라운드 모드 (`--background`)
- `/gemini:task`, `/gemini:rescue`, `/gemini:adversarial-review`
- `/gemini:result`, `/gemini:cancel`, `/gemini:status`, `/gemini:model`
- `gemini:gemini-rescue` 서브에이전트
- Review Gate (Stop hook)

**보존된 것**:
- ACP 모드 (gemini 상주 프로세스)
- 대화 히스토리 관리
- 보안 조치 (path traversal, shell injection 차단 등)

## 라이선스

Apache-2.0 (원본 라이선스 유지). LICENSE 파일 참고.
