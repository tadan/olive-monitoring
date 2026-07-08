# PRD Status — Olive Monitoring SaaS Refactor

_One-screen progress view. The autonomous runner updates this when it changes a PRD's state. See `README.md` for the
lifecycle and `RUNNER.md` for how the build loop works._

**Last updated:** 2026-06-17 (initial authoring)

| PRD | Title | Status | Pri | Depends on | Owner |
|-----|-------|--------|-----|------------|-------|
| 000 | Engineering hygiene & CI foundation | 👀 in_review | P0 | — | autonomous |
| 001 | Auth foundation (FastAPI JWT) | ✅ approved | P0 | 000 | autonomous |
| 002 | Multi-tenancy data model | ✅ approved | P0 | 001 | autonomous |
| 003 | Tenant-scoped API refactor | 📝 draft | P1 | 001, 002 | autonomous |
| 004 | Frontend auth & app shell | 📝 draft | P1 | 003 | autonomous |
| 005 | Scientific validation dossier (olives) | ✅ approved · 🧑 human-in-loop | P1 | — | user |
| 006 | Deployment: Contabo/YunoHost | 📝 draft | P1 | 003 | autonomous |
| 007 | Data quality & uncertainty surfacing | 📝 draft | P2 | 003, 005 | autonomous |
| 008 | UX/UI & frontend polish | 🗄️ backlog | P3 | 004 | user |

Legend: ✅ approved · 🔨 in_progress · 👀 in_review (PR open) · 🏁 done · 📝 draft · 🗄️ backlog · 🧑 human-in-loop

## Eligible for the runner right now
- **PRD-000** (no deps) — start here.
- **PRD-001** (after 000 done).
- **PRD-005 T1+T2 only** (scaffolding), then STOP for user research.

## Build order (critical path)
`000 → 001 → 002 → 003 → 004` (foundation), with `005` (science, supervised) and `006` (deploy) in parallel once
their deps clear. `007` and `008` last.

## Review queue (PRs awaiting your merge)
_None yet._
