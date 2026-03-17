#!/bin/sh
# agora-code post-install setup
# Installs Claude Code hooks and copies the skill definition so Claude Code
# picks up the agora-code skill on next session start.

set -e

# Ensure agora-code binary is available
if ! command -v agora-code >/dev/null 2>&1; then
    echo "agora-code not found — installing..."
    pip install agora-code
fi

# Install hooks (.claude/settings.json + shell scripts)
agora-code install-hooks --claude-code

# Copy skill file so Claude Code surfaces agora-code as a skill
SKILL_SRC="$(dirname "$0")/skills/agora-code/SKILL.md"
SKILL_DEST="$HOME/.claude/skills/agora-code/SKILL.md"

if [ -f "$SKILL_SRC" ]; then
    mkdir -p "$(dirname "$SKILL_DEST")"
    cp "$SKILL_SRC" "$SKILL_DEST"
    echo "✅ Skill installed: $SKILL_DEST"
else
    echo "⚠️  Skill file not found at $SKILL_SRC — skipping"
fi
