# PRDs — Olive Monitoring SaaS Refactor

Each PRD is one **YAML** file (token-efficient, machine + human readable). The autonomous runner reads these to
decide what to build. `STATUS.md` is the at-a-glance index. `RUNNER.md` describes the autonomous build loop.

## Lifecycle

```
draft → approved → in_progress → in_review → done
                                     ↘ (PR opened, awaiting your merge)
backlog = intentionally deferred (e.g. UX polish)
```

- **Only `approved` PRDs are eligible** for the autonomous runner.
- The runner moves a PRD `approved → in_progress` when it starts, `in_progress → in_review` when it opens the PR.
- **You** move `in_review → done` by merging the PR. The runner never merges.

## YAML schema (fields)

```yaml
id: PRD-000              # stable id
title: string
status: draft|approved|in_progress|in_review|done|backlog
priority: P0|P1|P2|P3
depends_on: [PRD-xxx]    # runner skips until all deps are done
model: opus              # model tier for autonomous work
human_in_loop: false     # true = runner only scaffolds, user drives
owner: autonomous|user
problem: >               # why this exists
goal: >                  # the one-sentence outcome
scope: []                # what's in
out_of_scope: []         # what's explicitly not
deliverables: []         # concrete artifacts produced
tasks:                   # ordered, checkable units
  - {id: T1, desc: ..., done: false}
acceptance: []           # binary pass/fail criteria
test_plan: []            # how it's verified (green = PR gate)
branch: string           # suggested branch name
notes: >
```

## Conventions

- Keep tasks small enough that one fits comfortably inside a single autonomous Opus run (well under the daily budget).
- `acceptance` must be objectively checkable — the runner uses it (plus a green CI) as the gate before opening a PR.
- Edits to a PRD's `tasks[].done` and the PRD `status` are committed by the runner so progress is auditable in git.
