# How to Work This Project

The system is designed so agents build and **you review**. Your job is small but decisive:
merge good PRs, promote the next PRDs, and do the human-only work (the olive science, taste calls).

## The one rule
**`STATUS.md` is home base.** Every session — and every "where am I?" — starts there. It always shows what's
approved, what's in progress, what's a PR waiting for you, and what's next.

## Starting a new session (at the computer)
Paste this:
> "Continue olive-monitoring. Read `docs/prds/STATUS.md`, `RUNNER.md`, and `SESSION-2026-06-17.md`.
> Tell me: what's in review, what's next, and anything blocked on me."

Then run the cadence below.

## The cadence (each working session, ~10 min)
1. **Read** `STATUS.md`.
2. **Merge** any PR that's `in_review` and looks right → that PRD becomes `done`.
3. **Promote** the next drafts to `approved` once their `depends_on` are all `done`
   (e.g. approve PRD-003 after PRD-002 merges).
4. **Run / check** the autonomous runner (or let the daily cron do it).
5. **Feed** any PRD-005 olive-science findings you gathered.

## Away from the computer (the walk)
You can do the single most important step — **merging — entirely from your phone.**
- **GitHub mobile app:** read the PR diff, the checks (green = lint+tests passed), and **merge**.
  That alone keeps the whole pipeline moving without a laptop.
- **Listen** to the PRD episodes (`docs/prds/audio/episodes/`) to keep the plan loaded in your head.
- **Capture, don't build:** ideas, scope changes, priority flips → a voice memo or note. Paste them into the
  next session; don't try to act on them from the phone.
- **PRD-005 (olive science)** is the one task that needs *you* and a screen — Elicit + papers. Do it in a
  focused sitting, not on a walk. Until you fill that template, the runner will scaffold it and stop.

## What runs without you vs. what waits for you
| Agents do autonomously | Only you can do |
|---|---|
| PRD-000,001,002,003,004,006,007 — build on a branch, test, open a PR | **Merge** PRs (the gate) |
| Update `STATUS.md` + PRD task checkboxes | Promote drafts → approved |
| PRD-005 scaffolding (extract thresholds, build the research brief) | PRD-005 research (Elicit) + final dossier |
| | PRD-008 UX/taste decisions |
| | Provisioning Contabo / DNS (agents document, you execute) |

## Guardrails that protect you while away
- Agents **never merge** — nothing reaches `main` without your click.
- A **green CI** is required before a PR is mergeable — broken work can't sneak in.
- **One scoped task per day** caps spend near $10 and keeps PRs small enough to review on a phone.
- Cross-tenant isolation has a **test** — if data could leak, the build goes red.

## If you're ever lost
Open `STATUS.md` → look at "Review queue" and "Eligible for the runner right now". That's your to-do list.
