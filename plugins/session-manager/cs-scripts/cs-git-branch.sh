#!/bin/bash
# 인자: repo 절대경로. 브랜치 목록 fzf → git switch
repo="$1"
[ -z "$repo" ] && exit 0
cur=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
br=$(
    { git -C "$repo" branch --format='%(refname:short)' 2>/dev/null;
      git -C "$repo" branch -r --format='%(refname:short)' 2>/dev/null \
        | grep -v 'HEAD$' | grep -v '^origin$'; } \
    | awk '!seen[$0]++' \
    | fzf --layout=reverse --prompt="브랜치 전환 (현재: $cur)> " \
          --preview="git -C '$repo' log --oneline --graph --color=always -20 {}" \
          --preview-window='right:55%'
)
[ -z "$br" ] && exit 0
local_br=${br#origin/}
if git -C "$repo" switch "$local_br" 2>/dev/null || git -C "$repo" checkout "$local_br" 2>/dev/null; then
    echo "→ '$local_br' 전환 완료"
else
    echo "전환 실패: $local_br (커밋 안 된 변경 때문일 수 있음)"
fi
sleep 1.5
