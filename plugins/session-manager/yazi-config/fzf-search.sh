#!/bin/bash
# Ctrl+F: 파일 검색 후 yazi를 해당 파일 위치로 이동
if command -v fd >/dev/null 2>&1; then
  files=$(fd --type f \
    --exclude .git \
    --exclude node_modules \
    --exclude __pycache__ \
    --exclude .venv \
    --exclude venv \
    --exclude .next \
    --exclude .cache \
    --exclude dist \
    --exclude build \
    --exclude target \
    --exclude .pytest_cache \
    --exclude .mypy_cache \
    --exclude .ruff_cache \
    --exclude .idea \
    --exclude .vscode \
    --exclude miniconda3 \
    --exclude anaconda3 \
    --exclude .conda \
    --exclude .local \
    --exclude .cargo \
    --exclude .rustup \
    --exclude .npm \
    --exclude .nvm \
    --exclude .pyenv \
    --exclude site-packages \
    --exclude .claude \
    --exclude .config \
    --exclude .gem \
    --exclude .yarn \
    --exclude .docker)
else
  files=$(find . -maxdepth 6 -type f \
    -not -path "*/.*" \
    -not -path "*/node_modules/*" \
    -not -path "*/miniconda3/*" \
    -not -path "*/anaconda3/*" \
    -not -path "*/site-packages/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" \
    -not -path "*/target/*" \
    -not -path "*/venv/*")
fi

selected=$(echo "$files" | fzf \
  --height 60% --border \
  --prompt "파일 검색> " \
  --preview "cat -- {}" \
  --preview-window "right:50%:wrap" \
  </dev/tty)

if [ -n "$selected" ]; then
  abs=$(realpath "$selected")
  ya emit reveal "$abs" 2>/dev/null
fi
