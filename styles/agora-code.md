---
name: agora-code
description: Persistent memory mode — automatically injects session context and enforces token-efficient file reading
keep-coding-instructions: true
---

You have persistent memory via agora-code. Follow these rules every session:

1. **At session start** — run `agora-code inject` to load prior context before doing anything else.
2. **Before reading any file over ~100 lines** — run `agora-code summarize <file>` first. Never use the Read tool on a large file without summarizing first.
3. **When done with a task** — run `agora-code complete --summary "..."` to archive the session.

The hooks handle indexing, recall, and checkpointing automatically. Your only job is inject at start, summarize before large reads, and complete when done.
