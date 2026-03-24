---
description: Show current memex status — projects, sessions, gaps
---
## Project Index

!`cat projects/INDEX.md`

## Session Counts

!`echo "=== Summarized ===" && find projects -name "*.md" -not -name "README.md" -not -name "INDEX.md" | wc -l && echo "=== Raw sessions (local) ===" && find history/local/projects -name "*.jsonl" -not -path "*/subagents/*" 2>/dev/null | wc -l && echo "=== Raw sessions (remote) ===" && find history/remote -name "*.jsonl" -not -path "*/subagents/*" 2>/dev/null | wc -l && echo "=== History size ===" && du -sh history/ 2>/dev/null`

Report the current state of memex:
- How many projects are tracked
- How many sessions are summarized vs. raw
- Any gaps (sessions not yet processed)
- Any remote machines configured but not yet synced
