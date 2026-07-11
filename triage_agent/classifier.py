import json
import os
from dataclasses import dataclass

import anthropic

from triage_agent.prompts import (
    ALLOWED_PRIORITIES,
    ALLOWED_TYPES,
    SYSTEM_PROMPT,
    build_user_message,
)

DEFAULT_MODEL = os.environ.get("TRIAGE_MODEL", "claude-sonnet-5")
DEFAULT_MAX_TOKENS = 1024


@dataclass
class TriageResult:
    summary: str
    type: str
    priority: str
    labels: list[str]


_FALLBACK_RESULT = TriageResult(
    summary="Unable to automatically summarize this issue.",
    type="question",
    priority="medium",
    labels=[],
)


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def _parse_response(raw_text: str, allowed_labels: list[str]) -> TriageResult:
    try:
        data = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        return _FALLBACK_RESULT

    summary = data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        summary = _FALLBACK_RESULT.summary

    issue_type = data.get("type")
    if issue_type not in ALLOWED_TYPES:
        issue_type = _FALLBACK_RESULT.type

    priority = data.get("priority")
    if priority not in ALLOWED_PRIORITIES:
        priority = _FALLBACK_RESULT.priority

    raw_labels = data.get("labels")
    if not isinstance(raw_labels, list):
        raw_labels = []
    allowed_set = set(allowed_labels)
    labels = [label for label in raw_labels if isinstance(label, str) and label in allowed_set]

    return TriageResult(summary=summary, type=issue_type, priority=priority, labels=labels)


def classify_issue(
    title: str,
    body: str,
    allowed_labels: list[str],
    client: anthropic.Anthropic | None = None,
) -> TriageResult:
    client = client or _get_client()
    user_message = build_user_message(title, body, allowed_labels)

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=DEFAULT_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text if response.content else ""
    return _parse_response(raw_text, allowed_labels)
