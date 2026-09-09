# PRD Status — Olive Monitoring SaaS Refactor

_One-screen progress view. The autonomous runner updates this when it changes a PRD's state. See `README.md` for the
lifecycle and `RUNNER.md` for how the build loop works._

**Last updated:** 2026-07-14

| PRD | Title | Status | Pri | Depends on | Owner | Linear |
|-----|-------|--------|-----|------------|-------|--------|
| 000 | Engineering hygiene & CI foundation | 🏁 done | P0 | — | autonomous | [DAN-5](https://linear.app/daniele-tatasciore/issue/DAN-5) |
| 001 | Auth foundation (FastAPI JWT) | 🔨 in_progress | P0 | 000 | autonomous | [DAN-6](https://linear.app/daniele-tatasciore/issue/DAN-6) |
| 002 | Multi-tenancy data model | ✅ approved | P0 | 001 | autonomous | [DAN-7](https://linear.app/daniele-tatasciore/issue/DAN-7) |
| 003 | Tenant-scoped API refactor | 📝 draft | P1 | 001, 002 | autonomous | [DAN-8](https://linear.app/daniele-tatasciore/issue/DAN-8) |
| 004 | Frontend auth & app shell | 📝 draft | P1 | 003 | autonomous | [DAN-9](https://linear.app/daniele-tatasciore/issue/DAN-9) |
| 005 | Scientific validation dossier (olives) | 🔨 in_progress · 🧑 human-in-loop | P1 | — | user | [DAN-10](https://linear.app/daniele-tatasciore/issue/DAN-10) |
| 006 | Deployment: Contabo/YunoHost | 📝 draft | P1 | 003 | autonomous | [DAN-11](https://linear.app/daniele-tatasciore/issue/DAN-11) |
| 007 | Data quality & uncertainty surfacing | 📝 draft | P2 | 003, 005 | autonomous | [DAN-12](https://linear.app/daniele-tatasciore/issue/DAN-12) |
| 008 | UX/UI & frontend polish | 🗄️ backlog | P3 | 004 | user | — |

Legend: ✅ approved · 🔨 in_progress · 👀 in_review (PR open) · 🏁 done · 📝 draft · 🗄️ backlog · 🧑 human-in-loop

## Eligible for the runner right now
- **PRD-001** — auth foundation, P0, no blockers.
- **PRD-005** — T1+T2 scaffolding DONE (2026-07-14). ⏸️ **Awaiting user (T3):** run Elicit and fill
  `docs/validation/elicit-research-brief.md`. Runner will not touch T4 until the template is filled.

## Build order (critical path)
`000 → 001 → 002 → 003 → 004` (foundation), with `005` (science, supervised) and `006` (deploy) in parallel once
their deps clear. `007` and `008` last.

## Review queue (PRs awaiting your merge)
_Nothing pending._
