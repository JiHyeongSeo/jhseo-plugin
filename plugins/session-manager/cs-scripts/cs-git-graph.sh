#!/bin/bash
# 인자: repo 절대경로
# fzf git graph + 커서 커밋 delta 미리보기
# Enter: 변경 파일 선택 → 전체 좌우 diff (VSCode 스타일)
repo="$1"
[ -z "$repo" ] && exit 0
CSDIR="$HOME/.config/cs"

git -C "$repo" log --oneline --graph --all --decorate --color=always 2>/dev/null \
| fzf --ansi --no-sort --layout=reverse --border \
    --prompt="graph> " \
    --header="Enter:파일선택→전체diff  q/Esc:닫기" \
    --preview="
        commit=\$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1)
        if [ -n \"\$commit\" ]; then
            git -C '$repo' show \"\$commit\" 2>/dev/null \
            | delta --side-by-side --width \"\${FZF_PREVIEW_COLUMNS:-80}\" 2>/dev/null
        else
            echo '(그래프 라인)'
        fi
    " \
    --preview-window="right:60%:wrap" \
    --bind="enter:execute(
        commit=\$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1)
        [ -n \"\$commit\" ] && bash '$CSDIR/cs-git-show.sh' '$repo' \"\$commit\"
    )" \
    --bind="q:abort"
