import json
import os
import sys

from triage_agent.classifier import TriageResult, classify_issue
from triage_agent.github_api import add_labels, get_repo_labels, post_comment

COMMENT_HEADER = "🤖 **Automated triage** (via claude-issue-triage-agent)"


def _load_event(event_path: str) -> dict:
    with open(event_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_comment(result: TriageResult) -> str:
    labels_line = ", ".join(result.labels) if result.labels else "none suggested"
    return (
        f"{COMMENT_HEADER}\n\n"
        f"**Type:** {result.type}\n"
        f"**Priority:** {result.priority}\n"
        f"**Summary:** {result.summary}\n"
        f"**Suggested labels:** {labels_line}"
    )


def run(event: dict, repo_full_name: str, github_token: str) -> str | None:
    """Triage the issue/PR in `event`. Returns a status message, or None if skipped."""
    if event.get("action") != "opened":
        return None

    if "pull_request" in event:
        kind, noun, item = "pull_request", "PR", event["pull_request"]
    elif "issue" in event:
        kind, noun, item = "issue", "issue", event["issue"]
    else:
        return None

    owner, repo = repo_full_name.split("/", 1)
    item_number = item["number"]
    title = item.get("title", "")
    body = item.get("body") or ""

    allowed_labels = get_repo_labels(owner, repo, github_token)
    result = classify_issue(title, body, allowed_labels, kind=kind)

    post_comment(owner, repo, item_number, _build_comment(result), github_token)
    add_labels(owner, repo, item_number, result.labels, github_token)

    return (
        f"Triaged {noun} #{item_number}: type={result.type} "
        f"priority={result.priority} labels={result.labels}"
    )


def main() -> int:
    event = _load_event(os.environ["GITHUB_EVENT_PATH"])
    repo_full_name = os.environ["GITHUB_REPOSITORY"]
    github_token = os.environ["GITHUB_TOKEN"]

    status = run(event, repo_full_name, github_token)
    print(status or "Not a newly opened issue/PR event; nothing to do.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
