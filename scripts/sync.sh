#!/usr/bin/env bash
# sync.sh — Pull .claude history from remote machines via Tailscale/SSH
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMEX_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG="$MEMEX_DIR/config.yaml"
REMOTE_DIR="$MEMEX_DIR/history/remote"

if [ ! -f "$CONFIG" ]; then
    echo "Error: config.yaml not found at $CONFIG"
    exit 1
fi

# Check Tailscale is running
if ! command -v tailscale &>/dev/null; then
    echo "Warning: tailscale CLI not found. Attempting SSH anyway..."
elif ! tailscale status &>/dev/null; then
    echo "Warning: Tailscale may not be connected. Attempting SSH anyway..."
fi

# Parse machines from config.yaml
MACHINES=$(python3 -c "
import yaml, json
with open('$CONFIG') as f:
    cfg = yaml.safe_load(f)
machines = cfg.get('machines', [])
if machines:
    print(json.dumps(machines))
else:
    print('[]')
" 2>/dev/null)

if [ "$MACHINES" = "[]" ] || [ -z "$MACHINES" ]; then
    echo "No machines configured in config.yaml"
    echo ""
    echo "Add machines like this:"
    echo "  machines:"
    echo "    - name: lab-server"
    echo "      host: lab-server.tailnet-name.ts.net"
    echo "      user: your-username"
    echo "      claude_dir: ~/.claude"
    exit 0
fi

# Sync each machine
echo "$MACHINES" | python3 -c "
import json, sys, subprocess, os

machines = json.loads(sys.stdin.read())
remote_dir = '$REMOTE_DIR'

for m in machines:
    name = m['name']
    host = m['host']
    user = m.get('user', 'your-username')
    claude_dir = m.get('claude_dir', '~/.claude')
    dest = os.path.join(remote_dir, name)
    os.makedirs(dest, exist_ok=True)

    print(f'Syncing {name} ({user}@{host})...')

    # Sync history.jsonl
    src_history = f'{user}@{host}:{claude_dir}/history.jsonl'
    r = subprocess.run(['rsync', '-az', '--timeout=30', src_history, f'{dest}/'],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f'  history.jsonl OK')
    else:
        print(f'  history.jsonl FAILED: {r.stderr.strip()}')

    # Sync projects/ (only JSONL and index files)
    src_projects = f'{user}@{host}:{claude_dir}/projects/'
    r = subprocess.run(['rsync', '-az', '--timeout=30',
                        '--include=*/', '--include=*.jsonl',
                        '--include=sessions-index.json', '--exclude=*',
                        src_projects, f'{dest}/projects/'],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f'  projects/ OK')
    else:
        print(f'  projects/ FAILED: {r.stderr.strip()}')

    print()
print('Sync complete.')
"
