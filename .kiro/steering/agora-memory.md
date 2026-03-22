---
inclusion: always
---

# Persistent Memory via agora-memory MCP

You have access to the `agora-memory` MCP server for persistent memory across sessions. The shell hooks handle session inject and checkpointing automatically — you only need to call MCP tools for deeper work.

## What happens automatically (shell hooks, 0 credits)

- **Every prompt**: `agora-code inject` runs and prepends LEARNINGS + last session context to your input
- **Every agent stop**: `agora-code kiro-sync` parses the session, stores a compact summary as a learning, saves a checkpoint with the last goal
- **Spec task start/end**: inject and checkpoint fire automatically

## When to call MCP tools manually

| Situation | Tool |
|---|---|
| Need full structured session detail | `get_session_context` |
| Completed a meaningful step mid-session | `save_checkpoint` |
| Discovered something non-obvious | `store_learning` |
| Starting a task — check if solved before | `recall_learnings` |
| Session fully done | `complete_session` |
| About to read a large file | `summarize_file` → then `read_file_range` |
| Need a specific line range | `read_file_range` |
| Just edited a file, want symbols searchable | `index_file` |
| Save a finding for the whole team | `store_team_learning` |
| Search team-wide knowledge | `recall_team` |

## Rules

1. **Don't call `get_session_context` on every prompt** — inject already loads context via the shell hook. Only call it when you need the full structured detail (hypothesis, next steps, files changed).

2. **Before reading any file over ~100 lines**, call `summarize_file` to get the AST outline with function names and line numbers. Then use `read_file_range` for just the section you need. Saves 90%+ tokens.

3. **Call `save_checkpoint`** after meaningful steps — bug fixed, feature added, decision made. Include `goal`, `action`, `files_changed`.

4. **Call `store_learning`** for non-obvious discoveries — gotchas, API quirks, architectural constraints. These are searchable in all future sessions.

5. **Call `recall_learnings`** before starting a new task to check if it's been done before.

6. **Call `complete_session`** when the user says they're done.

## Example flow

```
Session start (inject already ran):
  → Only call get_session_context() if you need full structured detail

Before new task:
  → recall_learnings("auth token")   # solved before?

Reading a large file:
  → summarize_file("src/auth.py")    # get outline
  → read_file_range("src/auth.py", 45, 90)  # read just what's needed

After fixing a bug:
  → store_learning("JWT tokens expire in 15min, refresh is /auth/refresh")
  → save_checkpoint(goal="fix auth", action="fixed token expiry", files_changed=["auth.py"])

Session end:
  → complete_session(summary="Fixed auth + added retry logic")
```
