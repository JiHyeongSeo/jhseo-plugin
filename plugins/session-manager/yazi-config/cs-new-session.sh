#!/bin/bash
SCRIPT=$(realpath "$(which cs)")
CACHE="/tmp/claude-browser-cache.json"
RESULT="/tmp/cs-new-session-result.txt"
LIST="/tmp/cs-newdirs.txt"
YAZI_DIR="$(pwd)"
rm -f "$RESULT"

{
    echo "$YAZI_DIR"
    if [ -f "$CACHE" ]; then
        python3 -c "
import json
from pathlib import Path
try:
    sessions = json.loads(Path('$CACHE').read_text())
    for s in sessions:
        p = s.get('projectPath', '')
        if p and Path(p).is_dir():
            print(p)
except Exception:
    pass
" 2>/dev/null
    fi
    find "$HOME" -maxdepth 3 -type d \
        ! -path '*/.*' ! -path '*/node_modules/*' ! -path '*/__pycache__/*' 2>/dev/null
} | awk '!seen[$0]++' > "$LIST"

tmux display-popup -E -h 80% -w 80% -- bash -c "
    fzf --prompt='새 세션 경로: ' --reverse --border \
        --header='Enter:선택  Esc:취소' \
        < '$LIST' > '$RESULT'
"

if [ -s "$RESULT" ]; then
    DIR=$(cat "$RESULT")
    if [ -d "$DIR" ]; then
        python3 "$SCRIPT" --tmux-new-session-at "$DIR"
        # yazi 자체에 cd 신호 (--block 상태에서 send-keys 안 먹어서)
        ya emit cd "$DIR" 2>/dev/null
    fi
fi
