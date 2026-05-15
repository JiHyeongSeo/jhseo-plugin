#!/bin/bash
SCRIPT=$(realpath "$(which cs)")
CACHE="/tmp/claude-browser-cache.json"
RESULT="/tmp/cs-session-pick-result.txt"
rm -f "$RESULT"

tmux display-popup -E -h 90% -w 90% -- bash -c "
    python3 '$SCRIPT' --fzf-list-lines --sessions-cache '$CACHE' 2>/dev/null | \
    fzf --ansi --layout=reverse --border \
        --delimiter=\$'\t' --with-nth=1 \
        --header='Enter:열기 Ctrl-T:제목편집 Ctrl-D:삭제 Esc:취소' \
        --preview=\"python3 '$SCRIPT' --preview-session {-1} --sessions-cache '$CACHE'\" \
        --preview-window='right:50%:wrap' \
        --bind=\"ctrl-t:execute(python3 '$SCRIPT' --fzf-action edit-title {-1} --sessions-cache '$CACHE')+reload-sync(python3 '$SCRIPT' --fzf-list-lines --sessions-cache '$CACHE')\" \
        --bind=\"ctrl-d:execute(python3 '$SCRIPT' --fzf-action delete {-1} --sessions-cache '$CACHE')+reload-sync(python3 '$SCRIPT' --fzf-list-lines --sessions-cache '$CACHE')\" \
        > '$RESULT'
"

if [ -s "$RESULT" ]; then
    SESSION_ID=$(awk -F'\t' '{print $NF}' "$RESULT" | tr -d '[:space:]')
    if [ -n "$SESSION_ID" ]; then
        python3 "$SCRIPT" --tmux-split-open "$SESSION_ID" --sessions-cache "$CACHE"
    fi
fi
