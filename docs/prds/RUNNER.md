# Autonomous Runner — PR-gated, Opus, hard ~$10/day

How the unattended build loop works, and how the daily budget ceiling is enforced.

## Principles

- **PR-gated:** the runner works on a branch, runs lint+tests, opens a PR, and **stops**. It never merges.
  You merge (`in_review → done`) at your leisure.
- **Opus, low volume:** quality over throughput. Expect roughly **one PRD task per run**.
- **Hard ~$10/day:** enforced structurally, not by trusting mid-run token accounting (see below).
- **Approved-only:** the runner only touches PRDs with `status: approved` whose `depends_on` are all `done`.
- **Human-in-loop respected:** for PRDs with `human_in_loop: true`, the runner does only the tasks marked AGENT,
  then stops and waits for you.

## Budget enforcement — the structural approach

The harness budget is **per-turn**, not per-day, and a model can't precisely meter its own spend mid-run. So we cap
spend by **bounding work per day**, not by watching a token counter:

1. **One task per scheduled run.** A single scoped PRD task on Opus reliably costs well under $10.
2. **Schedule at most N runs/day** such that `N × worst-case-task-cost ≤ $10`. Start with **N = 1** (one run/day).
3. **Ledger file** `docs/prds/.runner-ledger.json` records each run: date, PRD, task, branch, PR url, and a
   coarse self-estimate of tokens. Before working, the runner reads the ledger; if a run already happened today
   (or the day's estimate is near the ceiling), it exits immediately without spending on implementation.
4. **Scope guard.** If the next task looks too large for one run/budget, the runner splits it into a follow-up task
   in the PRD and does only the first slice.

> The ledger's token estimate is advisory (transparency); the *real* guarantee is "≤ N small tasks/day".

## The loop (one run)

```
1. Read docs/prds/.runner-ledger.json → if today's quota used, EXIT.
2. Read STATUS.md + PRD files → pick highest-priority `approved` PRD with all deps `done`
   and an undone task (respect human_in_loop AGENT-only tasks).
3. git checkout -b <branch from PRD>  (or resume the PRD's branch).
4. Implement exactly ONE task. Update that task's done: true in the PRD YAML.
5. Run gate: ruff + pytest + frontend lint/test. If red → fix within this run or revert the task and log a blocker.
6. If all PRD tasks now done → set PRD status in_review; else leave in_progress.
7. Commit (code + PRD YAML + STATUS.md). Push. Open/Update PR via gh (never merge).
8. Append run to .runner-ledger.json. EXIT.
```

## Scheduling options (decide before activating)

- **Cron (recommended):** `CronCreate` a once-daily job that runs the loop autonomously. Simple, naturally caps to
  N=1/day. Set the prompt to: "Run one iteration of docs/prds/RUNNER.md."
- **/loop dynamic:** a self-paced loop for when you want a burst of runs during a supervised window — not for
  unattended daily ops (it's session-bound).

## What stays manual (the runner will NOT do)

- Merging PRs.
- Anything in a `human_in_loop` PRD beyond AGENT-tagged tasks (e.g. PRD-005 literature research).
- Activating infrastructure (Contabo provisioning, DNS) — it documents and prepares; you execute.
- Force-pushing or touching `main` directly.

## Activation checklist (when you're ready)

- [ ] Confirm N runs/day (start 1).
- [ ] `CronCreate` the daily job (prompt above).
- [ ] Confirm PRD-000, 001, 002, 005 are `approved` in STATUS.md.
- [ ] First run should pick PRD-000.
