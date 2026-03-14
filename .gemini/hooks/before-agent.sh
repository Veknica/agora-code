#!/bin/sh
# Gemini CLI BeforeAgent hook — inject fresh session context every turn.
#
# Fires before every agent turn (after user submits a prompt).
# Injects session state via hookSpecificOutput.additionalContext
# so the agent stays aware of session even after compaction.
#
# Input JSON: {"prompt":"...","session_id":"...","transcript_path":"...",...}
# Output JSON: {"hookSpecificOutput":{"additionalContext":"..."}} or {}

cat > /dev/null

CONTEXT=$(agora-code inject --quiet --level index 2>/dev/null)

if [ -n "$CONTEXT" ]; then
    ESCAPED=$(printf '%s' "$CONTEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null)
    printf '{"hookSpecificOutput":{"additionalContext":%s}}\n' "$ESCAPED"
else
    printf '{}\n'
fi
