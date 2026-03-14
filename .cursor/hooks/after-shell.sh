#!/bin/sh
# Cursor afterShellExecution hook — summarize large shell output.
#
# Fires after every shell command. If stdout is large (>5KB),
# truncate and inject a summary so the agent doesn't drown in output.
#
# Input JSON: {"command":"...","stdout":"...","stderr":"...","exit_code":0,...}
# Output JSON: {"additional_context":"..."} or {}

INPUT=$(cat)

STDOUT_LEN=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    print(len(d.get('stdout', '') or ''))
except Exception:
    print('0')
" 2>/dev/null)

THRESHOLD=5000

if [ "$STDOUT_LEN" -gt "$THRESHOLD" ] 2>/dev/null; then
    SUMMARY=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
stdout = d.get('stdout', '') or ''
cmd = d.get('command', '') or ''
lines = stdout.splitlines()
n = len(lines)

head = '\n'.join(lines[:15])
tail = '\n'.join(lines[-10:])
mid = f'\n... ({n - 25} lines omitted) ...\n' if n > 25 else ''
summary = f'[Shell output summarized — {n} lines, {len(stdout)} chars]\nCommand: {cmd}\n\n{head}{mid}{tail}'

print(json.dumps(summary))
" 2>/dev/null)
    printf '{"additional_context":%s}\n' "$SUMMARY"
else
    printf '{}\n'
fi
