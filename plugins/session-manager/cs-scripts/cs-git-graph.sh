#!/bin/bash
# 인자: repo 절대경로. tig로 graph + 히스토리 (없으면 git log --graph fallback)
repo="$1"
[ -z "$repo" ] && exit 0
cd "$repo" || exit 0
if command -v tig >/dev/null 2>&1; then
    tig
else
    git log --graph --oneline --all --decorate --color=always | less -R
fi
