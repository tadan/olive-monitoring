# Olive Monitoring working context

- Source repository: `tadan/olive-monitoring` (this repository).
- Linear project: [Olive Monitoring SaaS](https://linear.app/daniele-tatasciore/project/olive-monitoring-saas-76f4d838ed72). Use the live issue state; `docs/prds/STATUS.md` may lag behind.
- Production is the deployment on the Synology NAS. GitHub `main` and a local clone are development sources, not proof of what is running in production.
- Start work from current `main` on an issue-scoped branch. Run the relevant checks in `.github/workflows/ci.yml`, open a PR, and leave merging to the owner as described in `docs/prds/RUNNER.md`.
- Check the NAS deployment state before proposing a production change. Ask before deploying, changing production data, or sending external messages.
- Keep credentials out of repository files and task output.
