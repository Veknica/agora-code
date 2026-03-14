#!/bin/sh
# Cursor preToolUse:Read hook — intercept large file reads and return summaries.
# Fires before every Read tool call. Small files pass through; large files get
# an AST/regex summary written to a temp file, then the read is redirected there.
#
# Input JSON from Cursor: {"tool_name":"Read","tool_input":{"file_path":"..."},...}
# Output: {"permission":"allow"} or {"permission":"allow","updated_input":{"file_path":"<summary_path>"}}
#
# Workaround: Cursor's preToolUse "deny" + "agent_message" doesn't deliver the
# message to the agent. Instead, we write the summary to a temp file and rewrite
# the Read to point there. The agent sees the summary as the file content.

INPUT=$(cat)

FILE_PATH=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', {})
    if isinstance(ti, str):
        import json as j2
        ti = j2.loads(ti)
    print(ti.get('file_path') or ti.get('path') or '')
except Exception:
    print('')
" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
    printf '{"permission":"allow"}\n'
    exit 0
fi

RESULT=$(agora-code summarize "$FILE_PATH" --json-output 2>/dev/null)

if [ -z "$RESULT" ]; then
    printf '{"permission":"allow"}\n'
    exit 0
fi

ACTION=$(printf '%s' "$RESULT" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    print(d.get('action', 'allow'))
except Exception:
    print('allow')
" 2>/dev/null)

if [ "$ACTION" = "summarize" ]; then
    SUMMARY_PATH=$(printf '%s' "$RESULT" | python3 -c "
import sys, json, os, hashlib
d = json.loads(sys.stdin.read())
summary = d.get('summary', '')
orig = d.get('original_lines', 0)
toks = d.get('summary_tokens', 0)
file_path = '$FILE_PATH'

content = summary + '\n\n[File has ' + str(orig) + ' lines. Summary is ~' + str(toks) + ' tokens. To read specific sections, request line ranges with offset+limit.]'

summary_dir = '/tmp/agora-code-summaries'
os.makedirs(summary_dir, exist_ok=True)
name_hash = hashlib.md5(file_path.encode()).hexdigest()[:12]
basename = os.path.basename(file_path)
summary_file = os.path.join(summary_dir, f'{basename}.{name_hash}.summary.txt')

with open(summary_file, 'w') as f:
    f.write(content)
print(summary_file)
" 2>/dev/null)

    if [ -n "$SUMMARY_PATH" ] && [ -f "$SUMMARY_PATH" ]; then
        printf '{"permission":"allow","updated_input":{"file_path":"%s"}}\n' "$SUMMARY_PATH"
    else
        printf '{"permission":"allow"}\n'
    fi
else
    printf '{"permission":"allow"}\n'
fi
