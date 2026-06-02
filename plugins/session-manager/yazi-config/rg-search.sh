#!/bin/bash
# Ctrl+R: 파일 내 텍스트 검색 → 해당 라인에서 에디터로 열기

selected=$(
    rg --line-number --no-heading --color=always --smart-case '' 2>/dev/null \
    | fzf --ansi --layout=reverse --border \
          --prompt="텍스트 검색> " \
          --delimiter=: \
          --nth=3.. \
          --preview='bat --color=always --highlight-line {2} {1} 2>/dev/null || cat {1}' \
          --preview-window='right:50%:+{2}-5' \
          </dev/tty
)

[ -z "$selected" ] && exit 0

file=$(echo "$selected" | cut -d: -f1)
line=$(echo "$selected" | cut -d: -f2)
abs=$(realpath "$file" 2>/dev/null)
[ -z "$abs" ] && exit 0

ya emit reveal "$abs" 2>/dev/null

STATE_FILE="/tmp/claude-browser-state.json"
CENTER=$(python3 -c "
import json
from pathlib import Path
try:
    d = json.loads(Path('$STATE_FILE').read_text())
    print(d.get('center_pane_id', ''))
except Exception:
    pass
" 2>/dev/null)

if [ -n "$CENTER" ]; then
    PCMD=$(tmux display-message -p -t "$CENTER" "#{pane_current_command}" 2>/dev/null)
    PCMD=$(basename "$PCMD")
    if [[ "$PCMD" == "vi" || "$PCMD" == "vim" || "$PCMD" == "nvim" ]]; then
        tmux send-keys -t "$CENTER" Escape
        sleep 0.05
        tmux send-keys -t "$CENTER" ":e +${line} ${abs}" Enter
    else
        tmux send-keys -t "$CENTER" "vi +${line} \"${abs}\"" Enter
    fi
else
    vi "+${line}" "$abs" </dev/tty
fi
