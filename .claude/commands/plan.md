---
description: Review and update schedule — deadlines, milestones, and priorities
argument-hint: [optional: "add", "update", or a specific project name]
---

## Current Schedule

!`cat schedule/deadlines.md 2>/dev/null || echo "No schedule yet"`

## Recent Activity (last 7 days)

!`find projects -name "*.md" -not -name "README.md" -not -name "INDEX.md" 2>/dev/null | sort | tail -20`

Based on the current schedule and recent activity:

If "$ARGUMENTS" contains "add": Help the user add a new deadline or milestone.
If "$ARGUMENTS" contains "update": Review and update existing entries.
Otherwise: Provide an overview of upcoming deadlines, suggest priorities, and flag anything overdue.

Keep `schedule/deadlines.md` up to date. If a workspace is configured with a tasks directory, sync deadlines there too.
