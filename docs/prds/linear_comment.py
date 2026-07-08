#!/usr/bin/env python3
"""Post a comment to a Linear issue via the GraphQL API.

Usage:
  python linear_comment.py <linear_id> <comment_body>
  e.g. python linear_comment.py DAN-6 "Runner started T0 on branch DAN-6-prd-001-auth"

Requires LINEAR_API_KEY env var. Exits 0 silently if key is absent so the
runner workflow never fails just because Linear commenting is misconfigured.
"""
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.linear.app/graphql"


def gql(query: str, api_key: str) -> dict:
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Authorization": api_key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: linear_comment.py <linear_id> <body>")
        sys.exit(1)

    linear_id, body = sys.argv[1], sys.argv[2]
    api_key = os.environ.get("LINEAR_API_KEY", "")

    if not api_key:
        print(f"LINEAR_API_KEY not set — skipping comment on {linear_id}")
        return

    try:
        # Resolve display ID (DAN-6) → internal UUID
        result = gql(f'{{ issue(id: "{linear_id}") {{ id }} }}', api_key)
        issue_uuid = result["data"]["issue"]["id"]

        # Post the comment
        result = gql(
            f'mutation {{ commentCreate(input: {{ issueId: "{issue_uuid}", '
            f'body: "{escape(body)}" }}) {{ success }} }}',
            api_key,
        )
        ok = result.get("data", {}).get("commentCreate", {}).get("success", False)
        print(f"Linear comment on {linear_id}: {'posted' if ok else 'failed'}")
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        # Non-fatal — Linear commenting should never block the runner
        print(f"Linear comment skipped ({e})")


if __name__ == "__main__":
    main()
