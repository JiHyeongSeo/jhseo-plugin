---
description: Run a Gemini code review against local git state (synchronous only)
argument-hint: '[--base <ref>] [--scope auto|working-tree|branch]'
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(node:*), Bash(git:*)
---

Run a Gemini review through the shared built-in reviewer (SOL team variant — synchronous only).

Raw slash-command arguments:
`$ARGUMENTS`

Core constraints:
- This command is review-only. Do not fix issues, apply patches, or suggest changes.
- Your only job is to run the review and return Gemini's output verbatim to the user.
- **Synchronous execution only.** Never use `run_in_background`. The SOL team policy is to avoid background mode (`gemini-plugin-for-claude` background tracking has alert delivery issues).

Argument handling:
- Preserve the user's arguments exactly.
- Do not add extra review instructions or rewrite the user's intent.
- Always run with `--wait` semantics (foreground).

Execution:
- Run:
```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/gemini-companion.mjs" review --wait "$ARGUMENTS"
```
- Return the command stdout verbatim, exactly as-is.
- Do not paraphrase, summarize, or add commentary before or after it.
- Do not fix any issues mentioned in the review output (caller decides).
