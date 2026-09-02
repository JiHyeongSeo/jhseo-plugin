#!/usr/bin/env bash
# Export portable Cursor settings from this machine into the repo (home/ mirror).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/home"

CURSOR_USER="${XDG_CONFIG_HOME:-$HOME/.config}/Cursor/User"
CURSOR_HOME="$HOME/.cursor"

echo "==> Cursor backup → $ROOT/home/"

mkdir -p "$DEST/.config/Cursor/User" "$DEST/.cursor"

copy_if_exists() {
  local src="$1" dst="$2"
  if [[ -e "$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    cp -a "$src" "$dst"
    echo "  + $(realpath --relative-to="$HOME" "$src" 2>/dev/null || echo "$src")"
  fi
}

# IDE user settings
copy_if_exists "$CURSOR_USER/settings.json" "$DEST/.config/Cursor/User/settings.json"
copy_if_exists "$CURSOR_USER/keybindings.json" "$DEST/.config/Cursor/User/keybindings.json"
if [[ -d "$CURSOR_USER/snippets" ]]; then
  rm -rf "$DEST/.config/Cursor/User/snippets"
  cp -a "$CURSOR_USER/snippets" "$DEST/.config/Cursor/User/snippets"
  echo "  + .config/Cursor/User/snippets/"
fi

# CLI + global cursor home (portable only)
copy_if_exists "$CURSOR_HOME/cli-config.json" "$DEST/.cursor/cli-config.json"
copy_if_exists "$CURSOR_HOME/mcp.json" "$DEST/.cursor/mcp.json"
copy_if_exists "$CURSOR_HOME/hooks.json" "$DEST/.cursor/hooks.json"
if [[ -d "$CURSOR_HOME/rules" ]]; then
  rm -rf "$DEST/.cursor/rules"
  cp -a "$CURSOR_HOME/rules" "$DEST/.cursor/rules"
  echo "  + .cursor/rules/"
fi
if [[ -d "$CURSOR_HOME/hooks" ]]; then
  rm -rf "$DEST/.cursor/hooks"
  cp -a "$CURSOR_HOME/hooks" "$DEST/.cursor/hooks"
  echo "  + .cursor/hooks/"
fi

# Optional: project-level cursor config from a path argument
if [[ -n "${1:-}" && -d "$1/.cursor" ]]; then
  PROJ="$(realpath "$1")"
  SLUG="$(echo "$PROJ" | sed 's|^/||; s|/|-|g')"
  mkdir -p "$DEST/projects/$SLUG"
  rm -rf "$DEST/projects/$SLUG/.cursor"
  cp -aL "$PROJ/.cursor" "$DEST/projects/$SLUG/.cursor"
  echo "  + project .cursor from $PROJ (symlinks resolved)"
fi

echo ""
echo "Done. Review diff, then commit:"
echo "  cd $ROOT && git status && git diff home/"
