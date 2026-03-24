---
description: Collect local .claude history and identify new unsummarized sessions
---
## Collect Local History

!`./scripts/collect.sh`

## Current Session Files

!`find history/local/projects -name "*.jsonl" -not -path "*/subagents/*" | sort`

## Already Summarized

!`find projects -name "*.md" -not -name "README.md" -not -name "INDEX.md" | sort`

Compare the session files against the already-summarized list. Identify any NEW sessions that haven't been processed yet. For each new session, read the JSONL file, understand the conversation, and create a proper markdown summary following the conventions in CLAUDE.md.
