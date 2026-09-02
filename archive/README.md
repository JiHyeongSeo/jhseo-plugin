# Archive

The previous **SOL Team Claude/Gemini plugin monorepo** (`plugins/`, `docs/superpowers/`, etc.) was removed on migration to Cursor-only backup.

Recover old files from git history:

```bash
git log --oneline --max-count=5
git show pre-cursor-backup:README.md    # if tag exists
git checkout legacy/sol-plugins -- plugins/   # if branch was created
```

Or browse commit before the cleanup commit on `main`.
