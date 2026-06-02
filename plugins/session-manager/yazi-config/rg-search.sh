#!/bin/bash
# Ctrl+Shift+F: 파일 내 텍스트 검색 (ripgrep + fzf)
# 결과 선택 시 yazi가 해당 파일 위치로 이동

if ! command -v rg >/dev/null 2>&1; then
    if ! command -v grep >/dev/null 2>&1; then
        exit 1
    fi
    # grep fallback
    SEARCH_CMD="grep -r --line-number --with-filename"
    FILES=$(eval "$SEARCH_CMD '' ." 2>/dev/null)
else
    SEARCH_CMD="rg"
fi

# rg로 텍스트 검색 후 fzf로 선택
selected=$(
    rg --line-number --no-heading --color=always --smart-case '' 2>/dev/null \
    | fzf --ansi --layout=reverse --border \
          --prompt="텍스트 검색> " \
          --delimiter=: \
          --preview='bat --color=always --highlight-line {2} {1} 2>/dev/null || cat {1}' \
          --preview-window='right:50%:+{2}-5' \
          </dev/tty
)

if [ -n "$selected" ]; then
    file=$(echo "$selected" | cut -d: -f1)
    abs=$(realpath "$file" 2>/dev/null)
    [ -n "$abs" ] && ya emit reveal "$abs" 2>/dev/null
fi
