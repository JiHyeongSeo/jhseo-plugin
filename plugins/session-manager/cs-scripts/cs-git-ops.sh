#!/bin/bash
# git 조작 헬퍼 (cs-git-graph.sh에서 호출)
# 인자: op repo [commit]
op="$1"; repo="$2"; commit="$3"
[ -z "$op" ] || [ -z "$repo" ] && exit 0

_msg()   { echo -e "\n\033[1;33m$*\033[0m"; }
_ok()    { echo -e "\033[1;32m✓ $*\033[0m"; }
_err()   { echo -e "\033[1;31m✗ $*\033[0m"; }
_pause() { echo; read -r -p "Enter 닫기..." _; }

# 브랜치+태그 통합 목록 (접두어 포함)
_refs() {
    git -C "$repo" branch -a --format='[브랜치] %(refname:short)' 2>/dev/null | grep -v 'HEAD'
    git -C "$repo" tag 2>/dev/null | sed 's/^/[태그] /'
}
_local_refs() {
    git -C "$repo" branch --format='[브랜치] %(refname:short)' 2>/dev/null | grep -v 'HEAD'
    git -C "$repo" tag 2>/dev/null | sed 's/^/[태그] /'
}

case "$op" in

fetch)
    _msg "Fetching from all remotes..."
    git -C "$repo" fetch --all --prune 2>&1
    _ok "fetch 완료"
    _pause
    ;;

checkout)
    sel=$(_refs | fzf --layout=reverse --border \
        --prompt="체크아웃> " \
        --header="Enter:체크아웃  q/Esc:취소" \
        --bind="q:abort")
    [ -z "$sel" ] && exit 0
    target=$(echo "$sel" | sed 's/^\[브랜치\] //;s/^\[태그\] //')
    # remote 브랜치면 로컬 브랜치명만 추출
    local_target="${target#origin/}"
    git -C "$repo" checkout "$local_target" 2>&1 \
        || git -C "$repo" checkout -b "$local_target" --track "$target" 2>&1
    _pause
    ;;

new)
    # 브랜치 또는 태그 선택
    kind=$(printf '브랜치\n태그' | fzf --layout=reverse --border \
        --prompt="생성 종류> " --header="q/Esc:취소" --bind="q:abort")
    [ -z "$kind" ] && exit 0

    if [ "$kind" = "브랜치" ]; then
        cur=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
        read -r -p "새 브랜치 이름 (기반: ${commit:-$cur}): " name
        [ -z "$name" ] && exit 0
        if [ -n "$commit" ]; then
            git -C "$repo" checkout -b "$name" "$commit" 2>&1
        else
            git -C "$repo" checkout -b "$name" 2>&1
        fi
        _ok "브랜치 '$name' 생성 및 체크아웃"
    else
        read -r -p "태그 이름 (커밋: ${commit:-HEAD}): " name
        [ -z "$name" ] && exit 0
        read -r -p "태그 메시지 (없으면 lightweight): " msg
        if [ -n "$msg" ]; then
            git -C "$repo" tag -a "$name" "${commit:-HEAD}" -m "$msg" 2>&1
        else
            git -C "$repo" tag "$name" "${commit:-HEAD}" 2>&1
        fi
        _ok "태그 '$name' 생성"
    fi
    _pause
    ;;

delete)
    sels=$(_local_refs | fzf --layout=reverse --border --multi \
        --prompt="삭제> " \
        --header="Tab:다중선택  Enter:삭제  q/Esc:취소" \
        --bind="q:abort")
    [ -z "$sels" ] && exit 0
    echo "삭제 대상:"
    echo "$sels"
    read -r -p "삭제하시겠습니까? (y/N) " yn
    [ "$yn" != "y" ] && [ "$yn" != "Y" ] && exit 0
    while IFS= read -r line; do
        if echo "$line" | grep -q '^\[브랜치\]'; then
            br=$(echo "$line" | sed 's/^\[브랜치\] //')
            git -C "$repo" branch -D "$br" 2>&1
        elif echo "$line" | grep -q '^\[태그\]'; then
            tg=$(echo "$line" | sed 's/^\[태그\] //')
            git -C "$repo" tag -d "$tg" 2>&1
            read -r -p "리모트에서도 삭제? (y/N) " del_remote
            if [ "$del_remote" = "y" ] || [ "$del_remote" = "Y" ]; then
                git -C "$repo" push origin ":refs/tags/$tg" 2>&1
            fi
        fi
    done <<< "$sels"
    _ok "삭제 완료"
    _pause
    ;;

push)
    force_flag=""
    if [ "${@: -1}" = "--force" ]; then
        force_flag="--force-with-lease"
        _msg "⚠ Force push 모드 (--force-with-lease)"
    fi
    sels=$(_local_refs | fzf --layout=reverse --border --multi \
        --prompt="${force_flag:+[FORCE] }push> " \
        --header="Tab:다중선택  Enter:push  q/Esc:취소" \
        --bind="q:abort")
    [ -z "$sels" ] && exit 0
    if [ -n "$force_flag" ]; then
        read -r -p "Force push하시겠습니까? (y/N) " yn
        [ "$yn" != "y" ] && [ "$yn" != "Y" ] && exit 0
    fi
    while IFS= read -r line; do
        if echo "$line" | grep -q '^\[브랜치\]'; then
            br=$(echo "$line" | sed 's/^\[브랜치\] //')
            _msg "Pushing branch '$br' ${force_flag}..."
            git -C "$repo" push --set-upstream origin "$br" $force_flag 2>&1
        elif echo "$line" | grep -q '^\[태그\]'; then
            tg=$(echo "$line" | sed 's/^\[태그\] //')
            _msg "Pushing tag '$tg'..."
            git -C "$repo" push origin "$tg" $force_flag 2>&1
        fi
    done <<< "$sels"
    _ok "push 완료"
    _pause
    ;;

rebase)
    cur=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
    sel=$(git -C "$repo" branch -a --format='%(refname:short)' 2>/dev/null \
        | grep -v "^${cur}$\|HEAD" \
        | fzf --layout=reverse --border \
            --prompt="rebase 기준 브랜치> " \
            --header="현재: $cur  |  Enter:rebase  q/Esc:취소" \
            --bind="q:abort")
    [ -z "$sel" ] && exit 0
    _msg "Rebasing '$cur' onto '$sel'..."
    git -C "$repo" rebase "$sel" 2>&1
    _pause
    ;;


merge)
    cur=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
    sel=$(git -C "$repo" branch -a --format='%(refname:short)' 2>/dev/null \
        | grep -v "^${cur}$\|HEAD" \
        | fzf --layout=reverse --border \
            --prompt="merge할 브랜치> " \
            --header="현재: $cur  |  Enter:merge  q/Esc:취소" \
            --bind="q:abort")
    [ -z "$sel" ] && exit 0
    _msg "Merging '$sel' into '$cur'..."
    git -C "$repo" merge "$sel" 2>&1
    _pause
    ;;
esac
