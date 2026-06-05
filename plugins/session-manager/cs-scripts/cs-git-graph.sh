#!/bin/bash
# 인자: repo 절대경로
# fzf git graph + 키 바인딩으로 git 조작
repo="$1"
[ -z "$repo" ] && exit 0
CSDIR="$HOME/.config/cs"
OPS="$CSDIR/cs-git-ops.sh"
POPUP="tmux display-popup -E -h 85% -w 80%"

git -C "$repo" log --oneline --graph --all --decorate --color=always 2>/dev/null \
| fzf --ansi --no-sort --layout=reverse --border \
    --prompt="graph> " \
    --header="Enter:diff  f:fetch  c:checkout  n:new  d:delete  p:push  r:rebase  m:merge  q:닫기" \
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
    --bind="f:execute($POPUP bash '$OPS' fetch '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="c:execute($POPUP bash '$OPS' checkout '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="n:execute($POPUP bash '$OPS' new '$repo' \$(echo {} | grep -oE '[a-f0-9]{7,}' | head -1))+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="d:execute($POPUP bash '$OPS' delete '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="p:execute($POPUP bash '$OPS' push '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="r:execute($POPUP bash '$OPS' rebase '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="m:execute($POPUP bash '$OPS' merge '$repo')+reload(git -C '$repo' log --oneline --graph --all --decorate --color=always)" \
    --bind="q:abort"
