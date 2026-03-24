# Memex

> A portable identity for Claude Code. Clone it anywhere, and Claude knows you.

Every Claude Code session starts cold. You re-explain your project, your conventions, your context. CLAUDE.md helps, but it's static and you maintain it by hand. Your real context — what you've been working on, what decisions you've made, what problems you've solved — lives scattered across conversation histories that Claude never sees again.

Memex fixes that. It's a git repo that **is** your Claude identity.

Clone it to any machine, and Claude instantly has your full context — your projects, your patterns, your priorities. Work with Claude, and the new knowledge flows back. Push, and every machine gets the update. Your understanding of each other compounds over time, across every machine you touch.

## The Cycle

```
   ┌─────── git push ◄──── collect & curate ◄──── work with Claude
   │                                                      ▲
   ▼                                                      │
GitHub (private)                                    Claude knows you
   │                                                      ▲
   ▼                                                      │
   └─────► git pull ────► ~/memex on any machine ─────────┘
```

On every machine:
1. **Pull** memex — Claude has your full context instantly
2. **Work** — Claude knows your projects, conventions, and history
3. **Collect** — new session history accumulates in local `~/.claude/`
4. **Curate** — Claude reads the new sessions and writes structured summaries
5. **Push** — all your other machines get the updated knowledge

The git repo is the identity. GitHub is the sync layer. Claude is the curator.

## Quick Start

### 1. Fork & Clone

Fork this repo on GitHub, then clone your fork:

```bash
# Clone YOUR fork (not the original)
git clone https://github.com/YOUR_USERNAME/memex.git ~/memex
cd ~/memex
```

This gives you your own private copy. Your chat history, project summaries, and schedule stay in your repo — not ours.

### 2. Set Up Your Identity

```bash
# Edit CLAUDE.md — tell Claude who you are
# Collect your local chat history
./scripts/collect.sh

# Open Claude Code — it reads CLAUDE.md and knows its role
claude

# Process your sessions
/project:collect
```

### 3. Push & Sync Across Machines

```bash
# Push your knowledge to your fork
git add -A && git commit -m "sync from this machine" && git push

# On another machine: pull and Claude knows you there too
git pull
```

> **Tip**: Make your fork private. It will contain your full conversation histories.

## What's Inside

Memex is not an app. It's a Claude Code project — a directory with the right structure, instructions, and tools so that Claude becomes your personal assistant when you `cd ~/memex && claude`.

```
memex/
├── CLAUDE.md             # Claude's identity — who you are, how to behave
├── workspaces.yaml       # External directories memex can operate on
├── config.yaml           # Remote machine sync configuration
│
├── .claude/
│   ├── settings.json     # Permissions (what Claude can/can't do)
│   ├── commands/         # Custom slash commands
│   ├── skills/           # Workflows Claude triggers automatically
│   ├── agents/           # Specialized subagents for parallel work
│   └── rules/            # Scoped instructions by file path
│
├── projects/             # Curated session summaries by project
│   └── INDEX.md
├── schedule/             # Deadlines and milestones
│   └── deadlines.md
├── history/              # Raw chat histories (JSONL)
│   ├── local/
│   └── remote/<machine>/
└── scripts/
    ├── collect.sh        # Copy local .claude history
    ├── sync.sh           # Pull from remote machines (Tailscale)
    └── summarize.py      # Utility parser
```

### Pre-configured `.claude/`

- **5 commands**: collect, sync, plan, push, status
- **2 skills**: session summarization, workspace sync (auto-triggered)
- **2 agents**: session reader, workspace operator (for parallel work)
- **2 rules**: summary format, project organization (scoped to `projects/`)
- **Permissions**: allow scripts and file ops, deny destructive commands

## Commands

| Command | What it does |
|---------|-------------|
| `/project:collect` | Pull local history, find and process new sessions |
| `/project:sync` | Pull remote history via Tailscale, process new sessions |
| `/project:plan` | Review/update schedule and deadlines |
| `/project:push` | Push content to external workspaces |
| `/project:status` | Overview of memex state |

## Workspaces

Memex can reach into your external project directories. Define them in `workspaces.yaml`:

```yaml
workspaces:
  - name: Research
    path: ~/projects/research
    role: research-hub
    operations:
      - read: "**/*"
      - write: tasks/, ideas/
```

Claude pushes relevant summaries, deadlines, and ideas to these directories — but only where you've explicitly allowed writes.

## Multi-Machine Sync

**Primary method: git.** Push memex to a private GitHub repo. Pull on every machine. This syncs the curated knowledge (projects, schedule, workspaces config).

**For raw history:** If you also want to sync the raw `.claude/` session files between machines that can't git-push, use [Tailscale](https://tailscale.com/) + the built-in `sync.sh` script. Add machines to `config.yaml` and run `/project:sync`.

## Customization

The most important file is **`CLAUDE.md`**. It defines Claude's identity in this repo. Tell it:
- Who you are and what you do
- What projects you're working on
- How you like to work

The more Claude knows about you, the better it serves you. And because memex is a git repo, that knowledge travels everywhere you do.

## Citation

If you use Memex in your work or find it useful, please cite:

```bibtex
@software{zhou2026memex,
  author       = {Gengze Zhou},
  title        = {Memex: A Portable Identity for Claude Code},
  year         = {2026},
  url          = {https://github.com/GengzeZhou/memex},
  license      = {MIT}
}
```

## License

MIT — see [LICENSE](LICENSE) for details.
