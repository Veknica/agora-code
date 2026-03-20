---
name: "agora-memory"
displayName: "Agora Memory"
description: "Persistent memory layer for AI coding agents — session context, learnings, and file history survive restarts and new conversations."
keywords: ["memory", "session", "checkpoint", "recall", "learning", "persist", "context", "agora"]
---

# Agora Memory Power

Persistent memory for Kiro. Your goals, discoveries, and file history survive context resets, new conversations, and IDE restarts.

## Onboarding

### Step 1: Verify agora-code is installed

Run in terminal:
```
agora-code --version
```

If not installed:
```
pip install git+https://github.com/thebnbrkr/agora-code.git
```

Then get the full path for hooks:
```
which agora-code
```

### Step 2: Install hooks automatically

Create the following hook files in `.kiro/hooks/`:

**`.kiro/hooks/agora-session-inject.kiro.hook`**
```json
{
  "enabled": true,
  "name": "agora: session inject",
  "description": "Inject last session context before every prompt",
  "version": "1",
  "when": {
    "type": "userPromptSubmit"
  },
  "then": {
    "type": "runCommand",
    "command": "agora-code inject --quiet 2>/dev/null || true",
    "timeout": 10
  }
}
```

**`.kiro/hooks/agora-checkpoint.kiro.hook`**
```json
{
  "enabled": true,
  "name": "agora: auto checkpoint",
  "description": "Save session checkpoint after every agent turn",
  "version": "1",
  "when": {
    "type": "agentStop"
  },
  "then": {
    "type": "runCommand",
    "command": "agora-code checkpoint --quiet 2>/dev/null || true",
    "timeout": 10
  }
}
```

**`.kiro/hooks/agora-pre-read.kiro.hook`**
```json
{
  "enabled": true,
  "name": "agora: summarize before read",
  "description": "Get AST outline before reading a file to save tokens",
  "version": "1",
  "when": {
    "type": "preToolUse",
    "toolName": "readCode"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Before reading this file, call summarize_file from agora-memory to get the AST outline with function names and line numbers. Then use read_file_range to read only the section relevant to the current task."
  }
}
```

**`.kiro/hooks/agora-post-write.kiro.hook`**
```json
{
  "enabled": true,
  "name": "agora: index after write",
  "description": "Index file symbols into memory DB after editing",
  "version": "1",
  "when": {
    "type": "postToolUse",
    "toolName": "fsWrite"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Call index_file from agora-memory for the file that was just written so its symbols are searchable in future sessions."
  }
}
```

**`.kiro/hooks/agora-task-inject.kiro.hook`**
```json
{
  "enabled": true,
  "name": "agora: inject before task",
  "description": "Load session context before each spec task starts",
  "version": "1",
  "when": {
    "type": "preTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "agora-code inject --quiet 2>/dev/null || true",
    "timeout": 10
  }
}
```

**`.kiro/hooks/agora-task-checkpoint.kiro.hook`**
```json
{
  "enabled": true,
  "name": "agora: checkpoint after task",
  "description": "Save progress after each spec task completes",
  "version": "1",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "agora-code checkpoint --quiet 2>/dev/null || true",
    "timeout": 10
  }
}
```

> **Note:** If `agora-code` is not on your PATH in Kiro, replace `agora-code` with the full path from `which agora-code` (e.g. `/Library/Frameworks/Python.framework/Versions/3.10/bin/agora-code`).

---

# Memory Tools

You have access to the `agora-memory` MCP server. Use these tools to maintain context across sessions.

## When to use each tool

| Situation | Tool |
|---|---|
| Starting a new conversation | `get_session_context` |
| Completed a meaningful step | `save_checkpoint` |
| Discovered something non-obvious | `store_learning` |
| Starting a task — check if already solved | `recall_learnings` |
| About to read a large file | `summarize_file` → then `read_file_range` |
| Just edited a file | `index_file` |
| Session fully done | `complete_session` |

## Rules

1. **Always call `get_session_context` at the start** of every new conversation. This loads what was being worked on last session.

2. **Call `save_checkpoint`** after any meaningful step — task done, bug fixed, decision made.

3. **Call `store_learning`** when you discover something non-obvious: a gotcha, a pattern, an API quirk, a constraint.

4. **Call `recall_learnings`** before starting a new task to check if it's been solved before.

5. **Call `summarize_file`** before reading any large file. Get the outline, then use `read_file_range` for just the section you need. Saves 90%+ tokens.

6. **Call `complete_session`** when the user says they're done.

## Example flow

```
Session start:
  → get_session_context()

Before new task:
  → recall_learnings("auth token")

Before reading a large file:
  → summarize_file("src/auth.py")
  → read_file_range("src/auth.py", 45, 120)

After fixing a bug:
  → store_learning("JWT tokens expire in 15min — refresh at /auth/refresh")
  → save_checkpoint(goal="...", action="fixed auth bug", files_changed=["auth.py"])

Session end:
  → complete_session(summary="Fixed auth + added retry logic")
```
