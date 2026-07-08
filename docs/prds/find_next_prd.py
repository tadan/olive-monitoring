#!/usr/bin/env python3
"""Find the next PRD eligible for the autonomous runner.

Exits 0 in all cases. Writes a blank prd_id to GITHUB_OUTPUT when nothing
should run (gh error, or no eligible PRD). The caller is responsible for
the daily budget check; this script only answers "which PRD is next?"

A PRD is considered done when:
  - status == 'done', OR
  - status == 'in_review' AND its branch was actually MERGED (not just
    closed/deleted without merging — Opus review finding).

Fail-closed: any gh CLI failure raises and we write a blank prd_id so the
runner never proceeds on incomplete information.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

PRDS_DIR = Path(__file__).parent
GH_LIMIT = 200  # raise if you ever have >200 open or merged PRs


def _gh(*args: str) -> list[dict]:
    """Run gh CLI, return parsed JSON list. Raises RuntimeError on failure."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed:\n{result.stderr.strip()}")
    return json.loads(result.stdout or "[]")


def merged_pr_branches() -> set[str]:
    """Branch names of PRs that were actually squash/merge-committed into main."""
    prs = _gh(
        "pr", "list",
        "--state", "merged",
        "--json", "headRefName",
        "--limit", str(GH_LIMIT),
    )
    return {pr["headRefName"] for pr in prs}


def load_prds() -> dict[str, dict]:
    prds = {}
    for f in sorted(PRDS_DIR.glob("PRD-*.yaml")):
        with open(f) as fp:
            prd = yaml.safe_load(fp)
        prds[prd["id"]] = prd
    return prds


def is_done(prd: dict, merged: set[str]) -> bool:
    status = prd.get("status", "")
    if status == "done":
        return True
    # in_review + branch was actually merged (closed-without-merge is NOT done)
    if status == "in_review" and prd.get("branch") in merged:
        return True
    return False


def _write_output(key: str, value: str) -> None:
    print(f"  {key}={value}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"{key}={value}\n")


def _bail(reason: str) -> None:
    print(reason)
    for key in ("prd_id", "prd_branch", "prd_human_in_loop"):
        _write_output(key, "" if key != "prd_human_in_loop" else "false")


def main() -> None:
    try:
        merged = merged_pr_branches()
    except RuntimeError as e:
        _bail(f"ERROR: {e}\nExiting safely — cannot determine merge state.")
        return

    prds = load_prds()
    done_ids = {id for id, p in prds.items() if is_done(p, merged)}
    print(f"Done PRDs: {sorted(done_ids) or 'none'}")

    eligible = [
        prd for id, prd in prds.items()
        if prd.get("status") == "approved"
        and all(dep in done_ids for dep in (prd.get("depends_on") or []))
    ]

    if not eligible:
        _bail("No eligible PRD — nothing to do.")
        return

    eligible.sort(key=lambda p: p.get("priority", "P9"))
    next_prd = eligible[0]
    print(f"Next PRD: {next_prd['id']} — {next_prd['title']}")

    _write_output("prd_id", next_prd["id"])
    _write_output("prd_branch", next_prd.get("branch", ""))
    _write_output("prd_human_in_loop", str(next_prd.get("human_in_loop", False)).lower())


if __name__ == "__main__":
    main()
