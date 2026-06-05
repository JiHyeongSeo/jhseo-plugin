#!/bin/bash
# 인자: repo 절대경로, 커밋 SHA
# 변경 파일 목록 fzf → 선택 시 전체 파일 좌우 delta diff
# q(less) → 파일 목록으로 복귀, q/Esc(fzf) → 종료
repo="$1"
commit="$2"
[ -z "$repo" ] || [ -z "$commit" ] && exit 0

files=$(git -C "$repo" diff-tree --no-commit-id -r --name-only "$commit" 2>/dev/null)
if [ -z "$files" ]; then
    echo "변경된 파일이 없습니다 (merge commit 또는 초기 커밋)"
    sleep 1.5
    exit 0
fi

while true; do
    sel=$(echo "$files" | fzf --layout=reverse --border \
        --prompt="파일 선택> " \
        --header="Enter:전체 좌우 diff  q/Esc:닫기" \
        --preview="git -C '$repo' diff '${commit}^'..'$commit' -- {} 2>/dev/null | delta --side-by-side --width \$FZF_PREVIEW_COLUMNS" \
        --preview-window="right:60%:wrap" \
        --bind="q:abort")
    [ -z "$sel" ] && break

    ext="${sel##*.}"
    old=$(mktemp --suffix=".${ext}")
    new=$(mktemp --suffix=".${ext}")
    git -C "$repo" show "${commit}^:${sel}" > "$old" 2>/dev/null || true
    git -C "$repo" show "${commit}:${sel}"  > "$new" 2>/dev/null || true
    git diff --no-index -U999999 -- "$old" "$new" | delta --side-by-side --line-numbers --paging=always
    rm -f "$old" "$new"
    # less q 후 → 루프 재시작 → 파일 목록으로 복귀
done
