#!/bin/bash
# Ctrl+J: fzf로 폴더 선택 후 yazi 이동
# ya emit cd는 nested popup에서 불안정 → YAZI_CWD 파일 경유 방식 사용
CACHE="/tmp/claude-browser-cache.json"
LIST="/tmp/cs-jumpdirs.txt"
RESULT="/tmp/cs-cd-jump-result.txt"
rm -f "$RESULT"

{
    echo "$PWD"
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

DIR=$(fzf --prompt='폴더 이동: ' --reverse --border \
    --header='Enter:이동  Esc:취소' < "$LIST")

if [ -n "$DIR" ] && [ -d "$DIR" ]; then
    # ya emit cd로 현재 yazi 인스턴스에 cd 신호
    ya emit cd "$DIR" 2>/dev/null || true
fi
