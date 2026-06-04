#!/bin/bash
# 인자: repo 절대경로. 수정 파일 목록 fzf → 선택 시 그 파일 delta diff
repo="$1"
[ -z "$repo" ] && exit 0

# 변경 파일 목록 (상태 마커 포함)
files=$(git -C "$repo" status --porcelain 2>/dev/null)
if [ -z "$files" ]; then
    echo "변경된 파일이 없습니다"
    echo "($repo)"
    sleep 1.5
    exit 0
fi

# "XY path" → fzf 표시. 미리보기는 path만 추출해서 diff
sel=$(
    echo "$files" \
    | fzf --ansi --layout=reverse --prompt="수정 파일> " \
          --header="Enter: 좌우 diff 보기" \
          --preview="f=\$(echo {} | cut -c4-); git -C '$repo' diff HEAD -- \"\$f\" 2>/dev/null | delta --side-by-side --width \$FZF_PREVIEW_COLUMNS 2>/dev/null | grep -q . && git -C '$repo' diff HEAD -- \"\$f\" 2>/dev/null | delta --side-by-side --width \$FZF_PREVIEW_COLUMNS || { echo '[untracked / 새 파일]'; bat --color=always \"$repo/\$f\" 2>/dev/null || cat \"$repo/\$f\" 2>/dev/null; }" \
          --preview-window='right:55%:wrap'
)
[ -z "$sel" ] && exit 0
f=$(echo "$sel" | cut -c4-)
if git -C "$repo" diff HEAD -- "$f" 2>/dev/null | grep -q .; then
    git -C "$repo" diff HEAD -- "$f" | delta --side-by-side --line-numbers --paging=always
else
    bat --paging=always "$repo/$f" 2>/dev/null || less "$repo/$f"
fi
