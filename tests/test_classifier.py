import json
from unittest.mock import MagicMock

from triage_agent.classifier import TriageResult, classify_issue
from triage_agent.prompts import build_user_message


def _make_client(response_text: str, with_thinking_block: bool = False) -> MagicMock:
    client = MagicMock()
    content_block = MagicMock()
    content_block.type = "text"
    content_block.text = response_text

    content = [content_block]
    if with_thinking_block:
        thinking_block = MagicMock(spec=["type", "thinking"])
        thinking_block.type = "thinking"
        thinking_block.thinking = "reasoning about the issue..."
        content = [thinking_block, content_block]

    client.messages.create.return_value = MagicMock(content=content)
    return client


def test_classify_issue_skips_leading_thinking_block():
    payload = {
        "summary": "Login button does nothing on Safari.",
        "type": "bug",
        "priority": "high",
        "labels": ["bug"],
    }
    client = _make_client(json.dumps(payload), with_thinking_block=True)

    result = classify_issue(
        title="t", body="b", allowed_labels=["bug"], client=client
    )

    assert result.type == "bug"
    assert result.labels == ["bug"]


def test_classify_issue_happy_path():
    payload = {
        "summary": "Login button does nothing on Safari.",
        "type": "bug",
        "priority": "high",
        "labels": ["bug", "safari"],
    }
    client = _make_client(json.dumps(payload))

    result = classify_issue(
        title="Login broken on Safari",
        body="Clicking login does nothing.",
        allowed_labels=["bug", "safari", "docs"],
        client=client,
    )

    assert result == TriageResult(
        summary=payload["summary"],
        type="bug",
        priority="high",
        labels=["bug", "safari"],
    )
    client.messages.create.assert_called_once()


def test_classify_issue_filters_labels_not_in_allowed_list():
    payload = {
        "summary": "Some issue.",
        "type": "feature",
        "priority": "low",
        "labels": ["bug", "made-up-label"],
    }
    client = _make_client(json.dumps(payload))

    result = classify_issue(
        title="t", body="b", allowed_labels=["bug"], client=client
    )

    assert result.labels == ["bug"]


def test_classify_issue_rejects_invalid_type_and_priority():
    payload = {
        "summary": "Some issue.",
        "type": "not-a-real-type",
        "priority": "urgent!!",
        "labels": [],
    }
    client = _make_client(json.dumps(payload))

    result = classify_issue(title="t", body="b", allowed_labels=[], client=client)

    assert result.type == "question"
    assert result.priority == "medium"


def test_classify_issue_falls_back_on_malformed_json():
    client = _make_client("not valid json at all")

    result = classify_issue(title="t", body="b", allowed_labels=["bug"], client=client)

    assert result.type == "question"
    assert result.priority == "medium"
    assert result.labels == []


def test_build_user_message_includes_title_body_and_labels():
    message = build_user_message("Title here", "Body here", ["bug", "docs"])

    assert "Title here" in message
    assert "Body here" in message
    assert "bug, docs" in message


def test_build_user_message_handles_empty_body():
    message = build_user_message("Title here", "", [])

    assert "(no description provided)" in message
    assert "(none available)" in message


def test_build_user_message_uses_pull_request_wording_for_that_kind():
    message = build_user_message("A PR title", "A PR body", ["bug"], kind="pull_request")

    assert "Pull request title: A PR title" in message
    assert "Pull request body:" in message
    assert "Kind: pull_request" in message


def test_classify_issue_passes_kind_through_to_prompt():
    payload = {
        "summary": "Fixes the login bug.",
        "type": "bug",
        "priority": "medium",
        "labels": ["bug"],
    }
    client = _make_client(json.dumps(payload))

    classify_issue(
        title="Fix login", body="b", allowed_labels=["bug"], client=client, kind="pull_request"
    )

    _, kwargs = client.messages.create.call_args
    user_message = kwargs["messages"][0]["content"]
    assert "Kind: pull_request" in user_message
