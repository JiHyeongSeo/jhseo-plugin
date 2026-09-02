#!/usr/bin/env bash
# Install personal skills listed in skills.manifest.yaml (requires npx + network).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/skills.manifest.yaml"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found — install Node.js first" >&2
  exit 1
fi

echo "==> Installing Cursor skills from $MANIFEST"

# Matt Pocock — full set
if grep -q 'mattpocock/skills' "$MANIFEST"; then
  echo "--- mattpocock/skills (all)"
  npx skills@latest add mattpocock/skills -a cursor -y
fi

# Taste skill — selected
if grep -q 'taste-skill' "$MANIFEST"; then
  echo "--- Leonxlnx/taste-skill"
  npx skills@latest add https://github.com/Leonxlnx/taste-skill -a cursor \
    --skill design-taste-frontend \
    --skill minimalist-ui \
    --skill redesign-existing-projects \
    -y
fi

# Copy template rules into a project if path given
if [[ -n "${1:-}" && -d "$1" ]]; then
  PROJ="$(realpath "$1")"
  mkdir -p "$PROJ/.cursor/rules"
  for f in "$ROOT/templates/rules/"*.mdc; do
    [[ -f "$f" ]] || continue
    cp -a "$f" "$PROJ/.cursor/rules/"
    echo "  + $(basename "$f") → $PROJ/.cursor/rules/"
  done
fi

echo "Done."
