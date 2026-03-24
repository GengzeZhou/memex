---
description: Push memex content to an external workspace
argument-hint: <workspace-name> <what-to-push>
---

## Workspace Configuration

!`cat workspaces.yaml`

## What to Push

The user wants to push content to: $ARGUMENTS

Rules:
1. Check `workspaces.yaml` to confirm the target workspace exists and allows writes
2. Only push to directories listed under `operations.write` for that workspace
3. Never overwrite existing files without asking — create new files or append
4. After pushing, note what was pushed

Common push operations:
- **deadlines → workspace**: Sync `schedule/deadlines.md` to a workspace's task directory
- **idea → workspace**: Move a research idea from session notes into a workspace's ideas folder
- **summary → workspace**: Push a session summary to a relevant project directory

Execute the push and confirm what was written.
