#!/usr/bin/env bash
# Remove legacy Claude/Gemini plugin monorepo from main (preserved on legacy/sol-plugins).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git show-ref --verify --quiet refs/heads/legacy/sol-plugins; then
  echo "Creating legacy/sol-plugins branch first..."
  git branch legacy/sol-plugins
fi

echo "Removing legacy paths from main (recover from legacy/sol-plugins):"
git rm -rf \
  plugins \
  docs \
  .superpowers \
  .claude-plugin \
  CLAUDE.md \
  GEMINI.md \
  gemini_update_skills.sh \
  2>/dev/null || true

# Remove if still on disk but not tracked
for p in plugins docs .superpowers .claude-plugin CLAUDE.md GEMINI.md gemini_update_skills.sh; do
  [[ -e "$p" ]] && rm -rf "$p" && echo "  removed $p"
done

echo "Done. Commit with: git commit -m 'chore: remove legacy claude-plugins monorepo'"
