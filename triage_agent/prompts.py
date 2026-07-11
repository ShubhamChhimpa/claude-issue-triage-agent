ALLOWED_TYPES = ["bug", "feature", "question", "docs"]
ALLOWED_PRIORITIES = ["low", "medium", "high"]

SYSTEM_PROMPT = f"""You triage incoming GitHub issues for a software project.

Given an issue title and body, respond with ONLY a JSON object (no markdown
fences, no extra text) with exactly these keys:

- "summary": a 1-2 sentence plain-English summary of the issue.
- "type": one of {ALLOWED_TYPES}.
- "priority": one of {ALLOWED_PRIORITIES}.
- "labels": an array of strings, each one drawn ONLY from the allowed labels
  list you are given. Pick zero or more labels that best fit. Never invent a
  label that isn't in the allowed list.
"""


def build_user_message(title: str, body: str, allowed_labels: list[str]) -> str:
    body = body or "(no description provided)"
    labels_line = ", ".join(allowed_labels) if allowed_labels else "(none available)"
    return (
        f"Issue title: {title}\n\n"
        f"Issue body:\n{body}\n\n"
        f"Allowed labels: {labels_line}"
    )
