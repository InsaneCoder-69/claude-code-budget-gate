# Claude Code Budget Gate

A lightweight budget-gating system for Claude Code multi-agent workflows.

> **The backstory:** I'm not an engineer. I'm a biotech student and the operations co-founder of a startup (CampusCollab). I kept hearing about people running multiple Claude agents together, and I kept hitting one wall — agents would burn through my Claude Pro limit and leave tasks half-finished. There was no fuel gauge. So over one long session, I designed this with Claude as my co-builder: I drove the architecture and decisions, Claude wrote and tested the code, and we shipped it together. If a non-engineer can build and verify a working dev tool through AI collaboration, that's the actual point of this repo. — Vatsal

## The problem
Claude Code's Pro/Max subscription quota is a black box. Agents spawned mid-task can hit the limit and leave your codebase half-built. There's no way to read your real remaining quota programmatically.

## What this does
- **Gates** every subagent spawn before it starts — blocks tasks that would breach your safety floor
- **Reconciles** real token usage from the session transcript after each agent finishes
- **Persists** a rolling 5-hour budget ledger shared across all agents
- **Free to run** — pure Python, reads local files, zero API cost

## How it workYou prompt Claude Code
-> budget_gate.py fires (PreToolUse hook) — enough budget?
-> YES: agent spawns and works
-> NO: blocked with a reason, task queued
-> agent finishes
-> reconcile.py fires (SubagentStop hook)
-> reads real token usage from the transcript
-> writes it back to the ledgers
It's a fuel gauge for a car that previously had none.

## Setup
Copy `.claude/` and `budget.py` into your project root, then every session:
```bash
cd your-project
export CLAUDE_PROJECT_DIR=$(pwd)
claude
```

## Tune it
Edit `budget.py`: `BUDGET_CAP` (tokens per window), `FLOOR` (reserve you never dip below), `WINDOW_HOURS`.

## Calibrate to reality
The ledger is a proxy for the black-box quota, so anchor it periodically:
```bash
# Run /usage in Claude Code, note the real % left, then:
python3 -c "import budget; l=budget.BudgetLedger.load(); l.calibrate(42)"
```

## The one assumption to verify
`reconcile.py` reads token usage from the Claude Code transcript (`message.usage`). This was confirmed working on v2.1.148. If a future version changes the format, the fix is isolated to one function: `extract_usage()`.

## Tested on
Claude Code v2.1.148 · macOS M2 · Claude Pro · Python 3.x — confirmed live: gate fired, agent ran, ledger logged real tokens, no double-counting.

## Windows
Works on Windows with two small changes. See [WINDOWS.md](WINDOWS.md).

## Built by
Vatsal Trivedi — non-engineer founder of CampusCollab. Designed, tested, and shipped end-to-end with Claude as co-builder. May 2026.

## License
MIT — fork it, use it, improve it.
