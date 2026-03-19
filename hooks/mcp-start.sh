#!/bin/sh
# Bootstrap agora-code binary if not installed, then start MCP server.
if ! which agora-code >/dev/null 2>&1; then
    pip install git+https://github.com/thebnbrkr/agora-code.git --quiet 2>/dev/null
fi
exec agora-code memory-server
