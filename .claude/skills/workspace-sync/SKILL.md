---
name: workspace-sync
description: >
  Sync content between memex and external workspaces. Use when the user
  mentions pushing content to a workspace, syncing deadlines, or moving ideas
  to external directories.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Workspace Sync Workflow

Reference @../../workspaces.yaml for workspace definitions.

### Sync Operations

**Deadlines sync** (bidirectional):
1. Read `schedule/deadlines.md` in memex
2. Read the corresponding deadlines file in the target workspace
3. Merge: take the more recent version of each entry, add new entries from either side
4. Write the merged result to both locations

**Idea migration** (memex → workspace):
1. When a session summary contains an idea worth developing
2. Extract the idea into a standalone markdown file
3. Write to the workspace's ideas directory
4. Link back to the original session summary

### Rules
- Never delete files in external workspaces
- Always check workspace write permissions before writing
- Log all sync operations
