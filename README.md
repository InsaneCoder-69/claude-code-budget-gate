# Claude Code Budget Gate

A lightweight budget-gating system for Claude Code multi-agent workflows.

## The problem
Claude Code's Pro/Max subscription quota is a black box. Agents spawned mid-task can hit the limit and leave your codebase half-built.

## What this does
- Gates every subagent spawn before it starts
- Reconciles real token usage from the session transcript after each agent finishes
- Persists a rolling 5-hour budget ledger shared across all agents
- Free to run — pure Python, zero API cost

## Setup
```bash
cd your-project
export CLAUDE_PROJECT_DIR=$(pwd)
claude
```

## Tune it
Edit `budget.py`: `BUDGET_CAP`, `FLOOR`, `WINDOW_HOURS`

## Tested on
Claude Code v2.1.148 · macOS M2 · Claude Pro · Python 3.x

## Built by
Vatsal Trivedi (CampusCollab) — non-engineer founder, built and tested end-to-end with Claude. May 2026.

## License
MIT
