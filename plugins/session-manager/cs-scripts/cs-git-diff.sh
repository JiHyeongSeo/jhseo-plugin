#!/bin/bash
# 인자: repo 절대경로. working tree diff를 delta 좌우로 표시
repo="$1"
[ -z "$repo" ] && exit 0
diff=$(git -C "$repo" diff HEAD 2>/dev/null)
if [ -z "$diff" ]; then
    echo "커밋되지 않은 변경사항이 없습니다 ($repo)"
    sleep 1.5
    exit 0
fi
echo "$diff" | delta --side-by-side --line-numbers --paging=always
