---
name: summarize-session
description: >
  Analyze a Claude Code session JSONL file and produce a structured markdown summary.
  Use PROACTIVELY when the user asks to process new sessions, when new history is
  collected, or when a session file path is mentioned.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

## Session Summarization Workflow

When given a session JSONL file:

1. **Read the file** — parse each line as JSON
2. **Filter to user/assistant messages** — skip `file-history-snapshot`, tool results, subagent internals
3. **Strip noise** — remove IDE tags (`<ide_opened_file>`), command outputs (`<local-command-stdout>`), system reminders, task notifications
4. **Identify the project** — from `cwd`, `project` field, or folder encoding
5. **Understand the task** — what was the user trying to accomplish?
6. **Document outcomes** — what was built, changed, fixed, or decided?
7. **Note technologies** — languages, frameworks, tools used

## Output Format

Follow the template in @SESSION_TEMPLATE.md

## Rules

- Be factual, not verbose. Summarize what happened, not what Claude said.
- Include enough detail that someone reading the summary months later can understand the work.
- If the session involves Chinese text, preserve key Chinese terms where they add context.
- If the session is trivial (<5 real messages, no meaningful work), write a 3-line summary in `misc/`.
- Always update the project README.md session table and projects/INDEX.md.
