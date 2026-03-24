#!/usr/bin/env python3
"""
summarize.py — Parse Claude Code session histories and generate per-project summaries.

Reads all JSONL session files from history/local/ and history/remote/*/,
groups conversations by project, and writes markdown summaries to summaries/.
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

MEMEX_DIR = Path(__file__).resolve().parent.parent
HISTORY_DIR = MEMEX_DIR / "history"
SUMMARIES_DIR = MEMEX_DIR / "summaries"


def parse_session_file(filepath: Path) -> list[dict]:
    """Parse a session JSONL file and extract user/assistant message pairs."""
    messages = []
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = entry.get("type")
                if msg_type not in ("user", "assistant"):
                    continue

                raw_message = entry.get("message", "")
                # message can be a string or a dict
                if isinstance(raw_message, str):
                    # Try to parse as JSON (sometimes stored as repr'd dict)
                    try:
                        raw_message = json.loads(raw_message.replace("'", '"'))
                    except (json.JSONDecodeError, ValueError):
                        pass

                # Extract text content
                content = ""
                if isinstance(raw_message, dict):
                    c = raw_message.get("content", "")
                    if isinstance(c, str):
                        content = c
                    elif isinstance(c, list):
                        # content blocks
                        parts = []
                        for block in c:
                            if isinstance(block, dict):
                                if block.get("type") == "text":
                                    parts.append(block.get("text", ""))
                                elif block.get("type") == "tool_use":
                                    parts.append(f"[tool: {block.get('name', '?')}]")
                            elif isinstance(block, str):
                                parts.append(block)
                        content = "\n".join(parts)
                elif isinstance(raw_message, str):
                    content = raw_message

                if not content.strip():
                    continue

                messages.append({
                    "type": msg_type,
                    "content": content.strip(),
                    "timestamp": entry.get("timestamp", ""),
                    "session_id": entry.get("sessionId", ""),
                    "cwd": entry.get("cwd", ""),
                })
    except Exception as e:
        print(f"  Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    return messages


def parse_history_jsonl(filepath: Path) -> dict:
    """Parse history.jsonl to get session metadata (project mapping, first prompts)."""
    sessions = {}
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                sid = entry.get("sessionId", "")
                project = entry.get("project", "")
                display = entry.get("display", "")
                timestamp = entry.get("timestamp", 0)

                if sid not in sessions:
                    sessions[sid] = {
                        "project": project,
                        "first_prompt": display,
                        "timestamp": timestamp,
                        "message_count": 0,
                    }
                sessions[sid]["message_count"] += 1
    except Exception as e:
        print(f"  Warning: Could not parse {filepath}: {e}", file=sys.stderr)
    return sessions


def find_all_sessions(history_dir: Path) -> dict:
    """Find all session files and group by source machine."""
    sources = {}

    # Local
    local_dir = history_dir / "local"
    if local_dir.exists():
        sources["local"] = local_dir

    # Remote machines
    remote_dir = history_dir / "remote"
    if remote_dir.exists():
        for machine_dir in remote_dir.iterdir():
            if machine_dir.is_dir():
                sources[machine_dir.name] = machine_dir

    return sources


def project_name_from_path(project_path: str) -> str:
    """Extract a clean project name from a project path."""
    if not project_path:
        return "misc"

    parts = Path(project_path).parts
    if not parts:
        return "misc"

    # Walk from the end, skip generic directory names
    skip = {"Desktop", "Documents", "projects", "~", "", "Users"}
    meaningful = []
    for part in reversed(parts):
        if part in skip:
            break
        meaningful.append(part)

    if not meaningful:
        return "misc"

    # Use up to 2 levels for context (e.g., "org--project-name")
    meaningful.reverse()
    if len(meaningful) >= 2:
        return f"{meaningful[-2]}--{meaningful[-1]}"
    return meaningful[0]


def collect_project_data(sources: dict) -> dict:
    """Collect all session data grouped by project."""
    projects = defaultdict(lambda: {
        "sessions": [],
        "machines": set(),
        "full_paths": set(),
    })

    for machine_name, base_dir in sources.items():
        # Parse history.jsonl for metadata
        history_file = base_dir / "history.jsonl"
        session_meta = {}
        if history_file.exists():
            session_meta = parse_history_jsonl(history_file)

        # Find all session JSONL files
        projects_dir = base_dir / "projects"
        if not projects_dir.exists():
            continue

        for jsonl_file in projects_dir.rglob("*.jsonl"):
            # Skip subagent files
            if "subagents" in str(jsonl_file):
                continue

            messages = parse_session_file(jsonl_file)
            if not messages:
                continue

            # Determine project from messages or metadata
            project_path = ""
            session_id = ""
            for msg in messages:
                if msg.get("cwd"):
                    project_path = msg["cwd"]
                if msg.get("session_id"):
                    session_id = msg["session_id"]
                if project_path and session_id:
                    break

            # Check history.jsonl metadata
            if session_id in session_meta:
                meta = session_meta[session_id]
                if meta["project"]:
                    project_path = meta["project"]

            # Fallback: decode project path from the folder name
            # Claude encodes paths like /Users/jane/Desktop/Foo as -Users-jane-Desktop-Foo
            if not project_path:
                rel = jsonl_file.relative_to(projects_dir)
                folder_name = rel.parts[0] if rel.parts else ""
                if folder_name.startswith("-"):
                    decoded = folder_name.replace("-", "/", 1).replace("-", "/")
                    project_path = decoded

            project_name = project_name_from_path(project_path)

            # Extract user messages only for summary
            user_messages = [m for m in messages if m["type"] == "user"]

            # Get timestamp range
            timestamps = [m["timestamp"] for m in messages if m["timestamp"]]
            date_range = ""
            if timestamps:
                try:
                    dates = []
                    for t in timestamps:
                        if isinstance(t, (int, float)):
                            dates.append(datetime.fromtimestamp(t / 1000))
                        elif isinstance(t, str):
                            dates.append(datetime.fromisoformat(t.replace("Z", "+00:00")))
                    if dates:
                        date_range = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}"
                except (ValueError, OSError):
                    pass

            projects[project_name]["sessions"].append({
                "session_id": session_id,
                "machine": machine_name,
                "messages": messages,
                "user_messages": user_messages,
                "date_range": date_range,
                "message_count": len(messages),
                "file": str(jsonl_file),
            })
            projects[project_name]["machines"].add(machine_name)
            if project_path:
                projects[project_name]["full_paths"].add(project_path)

    return dict(projects)


def generate_summary(project_name: str, data: dict) -> str:
    """Generate a markdown summary for a project."""
    sessions = data["sessions"]
    machines = data["machines"]
    full_paths = data["full_paths"]

    # Sort sessions by date
    sessions.sort(key=lambda s: s.get("date_range", ""))

    total_messages = sum(s["message_count"] for s in sessions)

    lines = [
        f"# {project_name}",
        "",
        f"**Sessions**: {len(sessions)} | **Messages**: {total_messages} | **Machines**: {', '.join(sorted(machines))}",
    ]

    if full_paths:
        lines.append(f"**Paths**: {', '.join(sorted(full_paths))}")

    lines.append("")
    lines.append("---")
    lines.append("")

    for i, session in enumerate(sessions, 1):
        lines.append(f"## Session {i}")
        if session["date_range"]:
            lines.append(f"**Date**: {session['date_range']} | **Machine**: {session['machine']}")
        lines.append("")

        # List user prompts as a conversation outline
        lines.append("### User Prompts")
        lines.append("")
        for msg in session["user_messages"]:
            # Truncate long messages
            content = msg["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            # Single line, quote format
            lines.append(f"- {content}")
        lines.append("")

    return "\n".join(lines)


def main():
    print(f"Memex Summarizer")
    print(f"================")
    print(f"History dir: {HISTORY_DIR}")
    print(f"Output dir:  {SUMMARIES_DIR}")
    print()

    sources = find_all_sessions(HISTORY_DIR)
    if not sources:
        print("No history found. Run collect.sh or sync.sh first.")
        sys.exit(1)

    print(f"Sources: {', '.join(sources.keys())}")
    print()

    projects = collect_project_data(sources)
    if not projects:
        print("No sessions found.")
        sys.exit(1)

    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    # Generate per-project summaries
    for project_name, data in sorted(projects.items()):
        summary = generate_summary(project_name, data)
        outfile = SUMMARIES_DIR / f"{project_name}.md"
        outfile.write_text(summary)
        print(f"  {project_name}: {len(data['sessions'])} sessions -> {outfile.name}")

    # Generate index
    index_lines = [
        "# Memex — Session Index",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Project | Sessions | Messages | Machines |",
        "|---------|----------|----------|----------|",
    ]
    for project_name, data in sorted(projects.items()):
        total_msgs = sum(s["message_count"] for s in data["sessions"])
        machines = ", ".join(sorted(data["machines"]))
        index_lines.append(
            f"| [{project_name}]({project_name}.md) | {len(data['sessions'])} | {total_msgs} | {machines} |"
        )

    index_file = SUMMARIES_DIR / "INDEX.md"
    index_file.write_text("\n".join(index_lines) + "\n")
    print(f"\n  Index -> {index_file.name}")
    print(f"\nDone. {len(projects)} projects summarized.")


if __name__ == "__main__":
    main()
