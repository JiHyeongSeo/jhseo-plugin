#!/bin/bash
# /tmp/cs-dashboard-dir.txt 의 디렉터리를 스캔 (없으면 HOME)
base=$(cat /tmp/cs-dashboard-dir.txt 2>/dev/null)
[ -z "$base" ] && base="$HOME"
[ ! -d "$base" ] && base="$HOME"
CS=$(realpath "$(which cs)" 2>/dev/null || echo "cs")
exec python3 "$CS" --git-status "$base"
