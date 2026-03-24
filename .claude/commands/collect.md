---
description: Collect local .claude history, detect new and updated sessions, and process them
---
## Collect Local History

!`./scripts/collect.sh`

## Session Manifest Status

!`python3 -c "
import json
from pathlib import Path

manifest_path = Path('projects/.manifest.json')
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

history_dir = Path('history/local')
new_sessions = []
updated_sessions = []
current_files = {}

for f in sorted(Path('history/local/projects').rglob('*.jsonl')):
    if 'subagents' in str(f):
        continue
    rel = str(f.relative_to('history/local'))
    lines = sum(1 for _ in open(f))
    current_files[rel] = lines

    if rel not in manifest:
        new_sessions.append((rel, lines))
    elif manifest[rel]['status'] == 'summarized' and lines > manifest[rel]['lines']:
        updated_sessions.append((rel, manifest[rel]['lines'], lines, manifest[rel].get('summary', '?')))
    elif manifest[rel]['status'] == 'pending':
        new_sessions.append((rel, lines))

if new_sessions:
    print('NEW SESSIONS (need summarizing):')
    for path, lines in new_sessions:
        print(f'  {lines:5d} lines  {path}')
    print()

if updated_sessions:
    print('UPDATED SESSIONS (summary needs refresh):')
    for path, old, new, summary in updated_sessions:
        print(f'  {old} -> {new} lines  {path}')
        print(f'    summary: {summary}')
    print()

if not new_sessions and not updated_sessions:
    print('All sessions are up to date.')
else:
    print(f'Total: {len(new_sessions)} new, {len(updated_sessions)} updated')
"
`

Process each session listed above:

**For NEW sessions**: Read the JSONL file, understand the conversation, create a markdown summary, and add an entry to the manifest.

**For UPDATED sessions**: Re-read the JSONL file, focusing on content AFTER the previously processed line count. Update the existing summary file to include the new work. Update the manifest with the new line count.

After processing, update `projects/.manifest.json` by running:

```python
manifest[rel_path] = {
    "lines": current_line_count,
    "last_timestamp": last_message_timestamp,
    "summary": "projects/ProjectName/YYYY-MM-DD_description.md",
    "status": "summarized"
}
```

If a session is trivial (<5 real messages, no meaningful work), mark it as `"status": "skipped"` in the manifest.
