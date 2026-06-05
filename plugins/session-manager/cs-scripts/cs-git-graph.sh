#!/bin/bash
# 인자: repo 절대경로
# fzf로 git graph + 커서 위치 커밋의 delta 사이드바이사이드 미리보기
# Enter: 해당 커밋 전체 delta diff (90% 팝업 없이 직접 표시)
repo="$1"
[ -z "$repo" ] && exit 0

git -C "$repo" log --oneline --graph --all --decorate --color=always 2>/dev/null \
| fzf --ansi --no-sort --layout=reverse --border \
    --prompt="graph> " \
    --header="Enter:커밋 diff  Esc:닫기" \
    --preview="
        commit=\$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1)
        if [ -n \"\$commit\" ]; then
            git -C '$repo' show \"\$commit\" 2>/dev/null \
            | delta --side-by-side --width \"\${FZF_PREVIEW_COLUMNS:-80}\" 2>/dev/null
        else
            echo '(merge 라인 또는 그래프 라인)'
        fi
    " \
    --preview-window="right:60%:wrap" \
    --bind="enter:execute(
        commit=\$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1)
        [ -n \"\$commit\" ] && git -C '$repo' show \"\$commit\" \
        | delta --side-by-side --line-numbers --paging=always
    )"
