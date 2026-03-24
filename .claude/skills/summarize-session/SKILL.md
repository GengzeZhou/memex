---
name: summarize-session
description: >
  Analyze a Claude Code session JSONL file and produce a structured markdown summary.
  Use PROACTIVELY when the user asks to process new sessions, when new history is
  collected, or when a session file path is mentioned.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

## Session Summarization Workflow

### For NEW sessions:

1. **Read the file** — parse each line as JSON
2. **Filter to user/assistant messages** — skip `file-history-snapshot`, tool results, subagent internals
3. **Strip noise** — remove IDE tags (`<ide_opened_file>`), command outputs (`<local-command-stdout>`), system reminders, task notifications
4. **Identify the project** — from `cwd`, `project` field, or folder encoding
5. **Understand the task** — what was the user trying to accomplish?
6. **Document outcomes** — what was built, changed, fixed, or decided?
7. **Note technologies** — languages, frameworks, tools used
8. **Write summary** — follow @SESSION_TEMPLATE.md
9. **Update manifest** — add entry to `projects/.manifest.json`

### For UPDATED sessions (session continued since last summary):

1. **Read the manifest** — find `lines` count from last processing
2. **Read the JSONL file** — focus on lines AFTER the previously processed count
3. **Read the existing summary** — understand what's already documented
4. **Identify new work** — what happened in the continuation?
5. **Update the summary** — append new sections or extend existing ones. Do NOT rewrite what's already there unless it's wrong.
6. **Update manifest** — set `lines` to current count

## Output Format

Follow the template in @SESSION_TEMPLATE.md

## Manifest Update

After processing, update `projects/.manifest.json`:

```python
manifest[rel_path] = {
    "lines": current_line_count,
    "last_timestamp": last_message_timestamp,
    "summary": "projects/ProjectName/YYYY-MM-DD_description.md",
    "status": "summarized"  # or "skipped" for trivial sessions
}
```

## Rules

- Be factual, not verbose. Summarize what happened, not what Claude said.
- Include enough detail that someone reading the summary months later can understand the work.
- If the session involves Chinese text, preserve key Chinese terms where they add context.
- If the session is trivial (<5 real messages, no meaningful work), mark as `"skipped"` in manifest.
- Always update the project README.md session table and projects/INDEX.md.
