#!/usr/bin/env bash
# collect.sh — Copy local ~/.claude history into memex/history/local/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMEX_DIR="$(dirname "$SCRIPT_DIR")"
HISTORY_DIR="$MEMEX_DIR/history/local"

# Read local claude_dir from config, default to ~/.claude
CLAUDE_DIR="${HOME}/.claude"
if command -v python3 &>/dev/null && [ -f "$MEMEX_DIR/config.yaml" ]; then
    CONFIGURED_DIR=$(python3 -c "
import yaml, os
try:
    with open('$MEMEX_DIR/config.yaml') as f:
        cfg = yaml.safe_load(f)
    d = cfg.get('local', {}).get('claude_dir', '~/.claude')
    print(os.path.expanduser(d))
except:
    print(os.path.expanduser('~/.claude'))
" 2>/dev/null)
    [ -n "$CONFIGURED_DIR" ] && CLAUDE_DIR="$CONFIGURED_DIR"
fi

if [ ! -d "$CLAUDE_DIR" ]; then
    echo "Error: Claude directory not found at $CLAUDE_DIR"
    exit 1
fi

echo "Collecting from: $CLAUDE_DIR"
echo "Destination:     $HISTORY_DIR"

# Copy history.jsonl
if [ -f "$CLAUDE_DIR/history.jsonl" ]; then
    cp "$CLAUDE_DIR/history.jsonl" "$HISTORY_DIR/"
    echo "  Copied history.jsonl"
fi

# Copy projects (session files)
if [ -d "$CLAUDE_DIR/projects" ]; then
    rsync -a --include='*/' --include='*.jsonl' --include='sessions-index.json' \
        --exclude='*' "$CLAUDE_DIR/projects/" "$HISTORY_DIR/projects/"
    echo "  Synced projects/"
fi

# Summary
JSONL_COUNT=$(find "$HISTORY_DIR" -name "*.jsonl" | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh "$HISTORY_DIR" 2>/dev/null | cut -f1)
echo ""
echo "Done. $JSONL_COUNT session files, $TOTAL_SIZE total."
