#!/bin/bash
# Ctrl+Shift+F: 파일 내 텍스트 검색 → 해당 라인에서 에디터로 열기

selected=$(
    rg --line-number --no-heading --color=always --smart-case '' 2>/dev/null \
    | fzf --ansi --layout=reverse --border \
          --prompt="텍스트 검색> " \
          --delimiter=: \
          --preview='bat --color=always --highlight-line {2} {1} 2>/dev/null || cat {1}' \
          --preview-window='right:50%:+{2}-5' \
          </dev/tty
)

[ -z "$selected" ] && exit 0

file=$(echo "$selected" | cut -d: -f1)
line=$(echo "$selected" | cut -d: -f2)
abs=$(realpath "$file" 2>/dev/null)
[ -z "$abs" ] && exit 0

# yazi를 해당 파일 위치로 이동
ya emit reveal "$abs" 2>/dev/null

# 현재 yazi pane의 상태 확인 후 center pane에서 에디터로 열기
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
        # 이미 vim 열려있으면 해당 파일+라인으로 이동
        tmux send-keys -t "$CENTER" Escape
        sleep 0.05
        tmux send-keys -t "$CENTER" ":e +${line} ${abs}" Enter
    else
        # 새로 열기
        tmux send-keys -t "$CENTER" "vi +${line} \"${abs}\"" Enter
    fi
else
    # center pane 없으면 yazi 안에서 직접 열기
    vi "+${line}" "$abs" </dev/tty
fi
