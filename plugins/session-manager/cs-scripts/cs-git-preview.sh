#!/bin/bash
# 인자: repo 절대경로. 대시보드 하단 미리보기 (변경 파일 + 최근 커밋)
repo="$1"
[ -z "$repo" ] && exit 0

# 변경 파일
changed=$(git -C "$repo" status -s 2>/dev/null)
echo -e "\033[1;33m■ 변경 파일\033[0m"
if [ -n "$changed" ]; then
    git -C "$repo" -c color.status=always status -s 2>/dev/null
else
    echo -e "  \033[90m(없음 - clean)\033[0m"
fi

echo ""
echo -e "\033[1;36m■ 최근 커밋\033[0m"
git -C "$repo" log --oneline --decorate --color=always -8 2>/dev/null \
    | sed 's/^/  /'
