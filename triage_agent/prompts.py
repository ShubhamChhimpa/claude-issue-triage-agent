ALLOWED_TYPES = ["bug", "feature", "question", "docs"]
ALLOWED_PRIORITIES = ["low", "medium", "high"]
ALLOWED_KINDS = ["issue", "pull_request"]

SYSTEM_PROMPT = f"""You triage incoming GitHub issues and pull requests for a software project.

Given a title and body (and whether it's an issue or a pull request), respond
with ONLY a JSON object (no markdown fences, no extra text) with exactly
these keys:

- "summary": a 1-2 sentence plain-English summary.
- "type": one of {ALLOWED_TYPES}. For a pull request, classify it by the kind
  of change it makes (e.g. a PR fixing a bug is "bug", one adding a feature
  is "feature").
- "priority": one of {ALLOWED_PRIORITIES}.
- "labels": an array of strings, each one drawn ONLY from the allowed labels
  list you are given. Pick zero or more labels that best fit. Never invent a
  label that isn't in the allowed list.
"""


def build_user_message(
    title: str, body: str, allowed_labels: list[str], kind: str = "issue"
) -> str:
    noun = "Pull request" if kind == "pull_request" else "Issue"
    body = body or "(no description provided)"
    labels_line = ", ".join(allowed_labels) if allowed_labels else "(none available)"
    return (
        f"Kind: {kind}\n\n"
        f"{noun} title: {title}\n\n"
        f"{noun} body:\n{body}\n\n"
        f"Allowed labels: {labels_line}"
    )
