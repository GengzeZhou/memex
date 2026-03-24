---
description: Sync history from remote machines via Tailscale and process new sessions
---
## Sync Remote Machines

!`./scripts/sync.sh`

## Check for New Remote Sessions

!`find history/remote -name "*.jsonl" -not -path "*/subagents/*" 2>/dev/null | sort`

## Already Summarized

!`find projects -name "*.md" -not -name "README.md" -not -name "INDEX.md" | sort`

Identify new sessions from remote machines that haven't been summarized yet. For each, read the JSONL, understand the conversation, create a session markdown, and update the project INDEX.
