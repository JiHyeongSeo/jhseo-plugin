#!/bin/bash
# Ctrl+J: fzf로 폴더 선택 후 yazi 이동만 (세션 생성 X)
CACHE="/tmp/claude-browser-cache.json"
RESULT="/tmp/cs-cd-jump-result.txt"
LIST="/tmp/cs-jumpdirs.txt"
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
    fzf --prompt='폴더 이동: ' --reverse --border \
        --header='Enter:이동  Esc:취소' \
        < '$LIST' > '$RESULT'
"

if [ -s "$RESULT" ]; then
    DIR=$(cat "$RESULT")
    [ -d "$DIR" ] && ya emit cd "$DIR" 2>/dev/null
fi
