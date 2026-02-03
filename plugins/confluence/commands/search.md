---
description: Confluence에서 문서를 검색합니다
---

# Confluence 검색

사용자가 요청한 검색어로 Confluence 문서를 검색합니다.

검색어: $ARGUMENTS

다음 명령어를 실행하여 검색하세요:
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py search "$ARGUMENTS" -s NAD -l 10
```

검색 결과의 `result_tree`를 사용자에게 트리 형태로 보여주세요.
