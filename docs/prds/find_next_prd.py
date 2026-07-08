#!/usr/bin/env python3
"""Find the next PRD eligible for the autonomous runner.

Prints the result and writes prd_id / prd_branch / prd_title to GITHUB_OUTPUT
if running inside GitHub Actions.  Exit 0 in all cases; a blank prd_id means
"nothing to do".

A PRD is considered effectively done if:
  - status == 'done', OR
  - status == 'in_review' AND its branch has no currently open PR
    (i.e. it was squash-merged and the branch was deleted).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

PRDS_DIR = Path(__file__).parent


def open_pr_branches() -> set[str]:
    result = subprocess.run(
        ["gh", "pr", "list", "--json", "headRefName", "--state", "open"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return {pr["headRefName"] for pr in json.loads(result.stdout or "[]")}


def load_prds() -> dict:
    prds = {}
    for f in sorted(PRDS_DIR.glob("PRD-*.yaml")):
        with open(f) as fp:
            prd = yaml.safe_load(fp)
        prds[prd["id"]] = prd
    return prds


def is_done(prd: dict, open_branches: set[str]) -> bool:
    status = prd.get("status", "")
    if status == "done":
        return True
    # Merged but YAML not yet updated: branch gone, was in_review
    if status == "in_review" and prd.get("branch") not in open_branches:
        return True
    return False


def _write_output(key: str, value: str) -> None:
    print(f"  {key}={value}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"{key}={value}\n")


def main() -> None:
    open_branches = open_pr_branches()
    prds = load_prds()

    done_ids = {id for id, p in prds.items() if is_done(p, open_branches)}
    print(f"Done PRDs: {sorted(done_ids) or 'none'}")

    eligible = []
    for id, prd in prds.items():
        if prd.get("status") != "approved":
            continue
        deps = prd.get("depends_on") or []
        if all(dep in done_ids for dep in deps):
            eligible.append(prd)

    if not eligible:
        print("No eligible PRD — nothing to do.")
        _write_output("prd_id", "")
        return

    eligible.sort(key=lambda p: p.get("priority", "P9"))
    next_prd = eligible[0]
    print(f"Next PRD: {next_prd['id']} — {next_prd['title']}")

    _write_output("prd_id", next_prd["id"])
    _write_output("prd_branch", next_prd.get("branch", ""))
    _write_output("prd_title", next_prd["title"])


if __name__ == "__main__":
    main()
