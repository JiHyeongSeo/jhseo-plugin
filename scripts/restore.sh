#!/usr/bin/env bash
# Restore Cursor settings from repo home/ mirror onto this machine.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/home"

CURSOR_USER="${XDG_CONFIG_HOME:-$HOME/.config}/Cursor/User"
CURSOR_HOME="$HOME/.cursor"

if [[ ! -d "$SRC" ]]; then
  echo "No backup found at $SRC — run ./scripts/backup.sh first" >&2
  exit 1
fi

echo "==> Restore Cursor settings from $ROOT"
echo "    Target: $HOME"
read -r -p "Continue? [y/N] " ans
[[ "$ans" =~ ^[Yy]$ ]] || exit 0

mkdir -p "$CURSOR_USER" "$CURSOR_HOME"

restore_if_exists() {
  local src="$1" dst="$2"
  if [[ -e "$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    if [[ -d "$src" ]]; then
      rm -rf "$dst"
      cp -a "$src" "$dst"
    else
      cp -a "$src" "$dst"
    fi
    echo "  → $dst"
  fi
}

restore_if_exists "$SRC/.config/Cursor/User/settings.json" "$CURSOR_USER/settings.json"
restore_if_exists "$SRC/.config/Cursor/User/keybindings.json" "$CURSOR_USER/keybindings.json"
restore_if_exists "$SRC/.config/Cursor/User/snippets" "$CURSOR_USER/snippets"
restore_if_exists "$SRC/.cursor/cli-config.json" "$CURSOR_HOME/cli-config.json"
restore_if_exists "$SRC/.cursor/mcp.json" "$CURSOR_HOME/mcp.json"
restore_if_exists "$SRC/.cursor/hooks.json" "$CURSOR_HOME/hooks.json"
restore_if_exists "$SRC/.cursor/rules" "$CURSOR_HOME/rules"
restore_if_exists "$SRC/.cursor/hooks" "$CURSOR_HOME/hooks"

# Optional project restore: ./scripts/restore.sh /path/to/project [slug]
if [[ -n "${1:-}" ]]; then
  PROJ="$(realpath "$1")"
  SLUG="${2:-$(echo "$PROJ" | sed 's|^/||; s|/|-|g')}"
  if [[ -d "$SRC/projects/$SLUG/.cursor" ]]; then
    mkdir -p "$PROJ"
    rm -rf "$PROJ/.cursor"
    cp -a "$SRC/projects/$SLUG/.cursor" "$PROJ/.cursor"
    echo "  → $PROJ/.cursor"
  else
    echo "  (no backed-up project .cursor for slug: $SLUG)" >&2
  fi
fi

echo ""
echo "Restart Cursor IDE / CLI. Then optionally:"
echo "  ./scripts/install-skills.sh"
