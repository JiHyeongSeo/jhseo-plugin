#!/bin/bash
# cs 멀티레포 git 대시보드 - 좌측 pane 메인 프로세스
CSDIR="$HOME/.config/cs"
YAZIDIR="$HOME/.config/yazi"
DIRFILE="/tmp/cs-dashboard-dir.txt"

if [ -n "$1" ]; then
    echo "$1" > "$DIRFILE"
elif [ ! -f "$DIRFILE" ]; then
    echo "$PWD" > "$DIRFILE"
fi

POPUP="tmux display-popup -E -h 90% -w 90%"
POPUP_SM="tmux display-popup -E -h 60% -w 70%"
STATUS="$CSDIR/cs-git-status-cur.sh"

while true; do
    "$STATUS" 2>/dev/null \
    | fzf --ansi --layout=reverse --border \
        --delimiter=$'\t' --with-nth=1 \
        --prompt="git> " \
        --header="Enter/g:graph+diff  d:전체diff  b:브랜치  ^E:yazi  ^R:새로고침  ^S:세션  ^N:새세션  ^Q:종료" \
        --preview="$CSDIR/cs-git-preview.sh {-1}" \
        --preview-window="down:55%:wrap:border-top" \
        --bind="enter:execute($POPUP $CSDIR/cs-git-graph.sh {-1})" \
        --bind="g:execute($POPUP $CSDIR/cs-git-graph.sh {-1})" \
        --bind="d:execute($POPUP $CSDIR/cs-git-diff.sh {-1})" \
        --bind="b:execute($POPUP_SM $CSDIR/cs-git-branch.sh {-1})" \
        --bind="start:reload($STATUS)" \
        --bind="ctrl-r:reload($STATUS)" \
        --bind="ctrl-e:execute($POPUP -d {-1} 'YAZI_CONFIG_HOME=$YAZIDIR yazi')" \
        --bind="ctrl-s:execute($YAZIDIR/cs-session-picker.sh)+reload($STATUS)" \
        --bind="ctrl-n:execute($YAZIDIR/cs-new-session.sh)+reload($STATUS)" \
        --bind="ctrl-q:execute-silent(tmux kill-session -t claude-browser)" \
        --bind="ctrl-z:execute-silent(tmux detach-client)"
    rc=$?
    if [ "$rc" -ne 0 ] && [ "$rc" -ne 130 ]; then
        break
    fi
    sleep 0.3
done
