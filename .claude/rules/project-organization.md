# Project Organization Rules

- One folder per project under `projects/`
- Project folder names: PascalCase or exact project name (e.g., `MyApp`, `data-pipeline`)
- Each project folder gets a `README.md` with: project description, metadata, session table
- `projects/INDEX.md` is the master index — keep it updated after every new session
- `projects/misc/` is for trivial one-off sessions
- Never modify files under `history/` — that's raw data, read-only reference
- When a project appears in `history.jsonl` but has no session JSONL, note it in INDEX.md under "Known Projects Without Session Files"
