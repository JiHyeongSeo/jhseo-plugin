#!/bin/bash
# 인자: repo 절대경로
# fzf git graph + 키 바인딩으로 git 조작 (이미 팝업 안이므로 nested popup 없이 직접 실행)
repo="$1"
[ -z "$repo" ] && exit 0
CSDIR="$HOME/.config/cs"
OPS="$CSDIR/cs-git-ops.sh"

_reload() {
    if [ -n "$(git -C "$repo" status --porcelain 2>/dev/null)" ]; then
        echo -e "\033[1;33m* \033[0m\033[1;33m[WIP]\033[0m 미커밋 변경사항 — Enter로 diff 확인"
    fi
    git -C "$repo" log --oneline --graph --all --decorate --color=always 2>/dev/null
}

_reload | fzf --ansi --no-sort --layout=reverse --border \
    --prompt="graph> " \
    --header="Enter:diff  f:fetch  c:checkout  n:new  d:delete  p:push  P:force-push  r:rebase  m:merge  q:닫기" \
    --preview="
        if echo {} | grep -q '\[WIP\]'; then
            git -C '$repo' status --short 2>/dev/null
            echo ''
            git -C '$repo' diff HEAD 2>/dev/null \
            | delta --side-by-side --width \"\${FZF_PREVIEW_COLUMNS:-80}\" 2>/dev/null
        else
            commit=\$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1)
            if [ -n \"\$commit\" ]; then
                git -C '$repo' show \"\$commit\" 2>/dev/null \
                | delta --side-by-side --width \"\${FZF_PREVIEW_COLUMNS:-80}\" 2>/dev/null
            else
                echo '(그래프 라인)'
            fi
        fi
    " \
    --preview-window="right:60%:wrap" \
    --bind="enter:execute(
        if echo {} | grep -q '\[WIP\]'; then
            bash '$CSDIR/cs-git-show.sh' '$repo' WIP
        else
            commit=\$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1)
            [ -n \"\$commit\" ] && bash '$CSDIR/cs-git-show.sh' '$repo' \"\$commit\"
        fi
    )" \
    --bind="f:execute(bash '$OPS' fetch '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="c:execute(bash '$OPS' checkout '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="n:execute(bash '$OPS' new '$repo' \$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1))+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="d:execute(bash '$OPS' delete '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="p:execute(bash '$OPS' push '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="r:execute(bash '$OPS' rebase '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="m:execute(bash '$OPS' merge '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="P:execute(bash '$OPS' push '$repo' '' '' --force)+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="q:abort"
