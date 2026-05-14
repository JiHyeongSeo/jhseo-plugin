#!/bin/bash
# yazi에서 Ctrl+S로 호출 - Claude 세션 선택해서 우측 pane에서 실행
SCRIPT=$(realpath "$(which cs)")
CACHE="/tmp/claude-browser-cache.json"
RESULT="/tmp/cs-session-pick-result.txt"
rm -f "$RESULT"

# tmux 팝업으로 fzf 실행 (선택 결과를 파일에 저장)
tmux display-popup -E -h 85% -w 85% -- bash -c "
    python3 '$SCRIPT' --fzf-list-lines --sessions-cache '$CACHE' 2>/dev/null | \
    fzf --ansi --layout=reverse --border \
        --delimiter=\$'\t' --with-nth=1 \
        --header='Claude 세션 선택 (Esc 취소)' > '$RESULT'
"

if [ -s "$RESULT" ]; then
    SESSION_ID=$(awk -F'\t' '{print $NF}' "$RESULT" | tr -d '[:space:]')
    if [ -n "$SESSION_ID" ]; then
        python3 "$SCRIPT" --tmux-split-open "$SESSION_ID" --sessions-cache "$CACHE"
    fi
fi
